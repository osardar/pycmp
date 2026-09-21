"""Supervised, persistent CPU encoder; the coordinator never imports Torch."""
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import signal
import tempfile
import time

import psutil

from .runtime import sha

MAX_OUTPUT = 16 * 1024**2


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def serve(connection, checkpoint, checkpoint_sha):
    os.setsid()
    try:
        import torch
        from .vendor.shared_model import SharedGraphEncoder, FEATURE_KEYS
        from .vendor.semantic import ProgramGraph, SCHEMA_VERSION
        torch.set_num_threads(1)
        if sha(checkpoint) != checkpoint_sha:
            raise ValueError("checkpoint changed before loading")
        state = torch.load(checkpoint, map_location="cpu", weights_only=True)
        config = state.get("config", {})
        if state.get("format") != 2 or config.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("checkpoint schema mismatch")
        if config.get("feature_keys") != list(FEATURE_KEYS):
            raise ValueError("checkpoint feature profile mismatch")
        model = SharedGraphEncoder(dimension=config["dimension"], layers=config["layers"],
            node_buckets=config["node_buckets"], relation_buckets=config["relation_buckets"])
        model.load_state_dict(state["model"])
        model.eval()
        del state
        if sha(checkpoint) != checkpoint_sha:
            raise ValueError("checkpoint changed during loading")
        connection.send({"ready": True, "dimension": config["dimension"],
                         "features": list(FEATURE_KEYS), "torch": torch.__version__})
    except Exception as exc:
        connection.send({"error": "configuration_error", "diagnostic": str(exc)[:1000]})
        return
    while True:
        try:
            request = connection.recv()
        except EOFError:
            return
        if request is None:
            return
        source, target, lane, include_units = request
        try:
            raw = Path(source).read_bytes()
            if len(raw) > MAX_OUTPUT:
                raise ValueError("output_limit")
            response = json.loads(raw)
            if "error" in response:
                connection.send(response)
                continue
            values = response["graphs"]
            node_cap, edge_cap = (10000, 100000) if lane == "source" else (100000, 500000)
            if not values or sum(len(g["nodes"]) for g in values) > node_cap:
                raise ValueError("node_limit")
            if sum(len(g["edges"]) for g in values) > edge_cap:
                raise ValueError("edge_limit")
            if lane == "bytecode" and any(g.get("metadata", {}).get("parser") != "native-dis-v1" or
                    any(n.get("attributes", {}).get("opcode") == "foreign_bytecode" for n in g["nodes"]) for g in values):
                raise ValueError("invalid bytecode graph profile")
            graphs = [ProgramGraph.from_dict(g) for g in values]
            with torch.inference_mode():
                vectors = model(graphs)
                mean = vectors.mean(0)
                if not torch.isfinite(vectors).all() or not torch.isfinite(mean).all() or mean.norm() <= 0:
                    raise ValueError("invalid_embedding")
                vector = torch.nn.functional.normalize(mean, dim=0)
            result = {"vector": vector.tolist(), "unit_count": len(graphs),
                      "node_count": sum(len(g.nodes) for g in graphs),
                      "edge_count": sum(len(g.edges) for g in graphs), "graph_sha256": digest(values)}
            if include_units:
                result["units"] = [{"unit_id": g.unit_id, "unit_kind": g.unit_kind, "vector": v.tolist()}
                                   for g, v in zip(graphs, vectors)]
            payload = canonical(result).encode()
            if len(payload) > MAX_OUTPUT:
                raise ValueError("output_limit")
            Path(target).write_bytes(payload)
            connection.send({"ok": True})
        except Exception as exc:
            code = str(exc)
            connection.send({"error": code if code in ("node_limit", "edge_limit", "output_limit", "invalid_embedding")
                             else "graph_failure", "diagnostic": code[:1000]})


class Encoder:
    def __init__(self, checkpoint, *, timeout=30, rss_limit=2 * 1024**3):
        self.checkpoint = str(Path(checkpoint).resolve())
        self.checkpoint_sha = sha(checkpoint)
        self.timeout, self.rss_limit = timeout, rss_limit
        self.process = self.connection = None
        self.start()

    def start(self):
        ctx = multiprocessing.get_context("spawn")
        self.connection, child = ctx.Pipe()
        self.process = ctx.Process(target=serve, args=(child, self.checkpoint, self.checkpoint_sha), daemon=True)
        self.process.start()
        child.close()
        try:
            self.config = self.wait()
            if not self.config.get("ready"):
                raise ValueError(self.config.get("diagnostic", "encoder failed to start"))
        except BaseException:
            self.close()
            raise

    def wait(self):
        deadline = time.monotonic() + self.timeout
        monitor = psutil.Process(self.process.pid)
        while time.monotonic() < deadline:
            try:
                if monitor.memory_info().rss > self.rss_limit:
                    return {"error": "memory_limit", "diagnostic": "inference RSS guard reached"}
            except psutil.NoSuchProcess:
                pass
            if self.connection.poll(.05):
                try:
                    return self.connection.recv()
                except EOFError:
                    break
            if not self.process.is_alive():
                break
        else:
            return {"error": "timeout", "diagnostic": "inference deadline reached"}
        return {"error": "worker_failure", "diagnostic": "inference worker exited"}

    def encode(self, parsed_path, lane, include_units):
        if self.process is None:
            self.start()
        with tempfile.TemporaryDirectory(prefix="pycmp-vector-") as directory:
            target = Path(directory) / "result.json"
            try:
                self.connection.send((str(parsed_path), str(target), lane, include_units))
                result = self.wait()
                if result.get("ok"):
                    with target.open("rb") as handle:
                        payload = handle.read(MAX_OUTPUT + 1)
                    if len(payload) > MAX_OUTPUT:
                        raise ValueError("inference output limit")
                    return json.loads(payload)
                if result.get("error") in ("timeout", "memory_limit", "worker_failure"):
                    self.close()
                return result
            except (BrokenPipeError, EOFError, ConnectionResetError):
                self.close()
                return {"error": "worker_failure", "diagnostic": "inference worker disconnected"}
            except BaseException:
                self.close()
                raise

    def close(self):
        if self.process is not None:
            if self.process.is_alive():
                try:
                    os.killpg(self.process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    self.process.kill()
            self.process.join(timeout=5)
            self.process.close()
            self.process = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None
