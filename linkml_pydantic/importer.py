import hashlib
import json
import sys
from importlib.abc import MetaPathFinder
from importlib.util import spec_from_file_location
from pathlib import Path
from typing import Optional, Sequence

from linkml.generators.pydanticgen.pydanticgen import MetadataMode, PydanticGenerator


class SchemaFinder(MetaPathFinder):
    """
    A meta path finder that allows the import machinery to import a .yaml linkml schema/

    Needs to be refactored into two classes so we can use properties rather than private
    methods that take the same arguments over and over again.

    References:
        - https://docs.python.org/3/reference/import.html#the-meta-path
        - https://docs.python.org/3/library/importlib.html#importlib.abc.MetaPathFinder

    """

    def find_spec(self, fullname, path, target=None):
        if path is None:
            return None
        yaml_file = self._yaml_file(fullname, path)
        if yaml_file is None:
            return None

        python_file = self._python_file(fullname, path)
        if not python_file.exists():
            # also hash the source and check for being outdated
            self.generate_module(yaml_file, python_file)
            self._update_hash(yaml_file, python_file, self._hash_file(path), fullname)
        else:
            existing_hashes = self._hashes(self._hash_file(path))
            module_hashes = self._generate_hash(yaml_file, python_file)
            if existing_hashes.get(fullname, {}).get("linkml", "") != module_hashes["linkml"]:
                self.generate_module(yaml_file, python_file)
                self._update_hash(yaml_file, python_file, self._hash_file(path), fullname)

        spec = spec_from_file_location(fullname, python_file)
        return spec

    def _yaml_file(self, fullname, path: Sequence[str]) -> Optional[Path]:
        file_parts = fullname.split(".")[1:]
        yaml_base = Path(path[0]).joinpath(*file_parts)
        yaml_files = [yaml_base.with_suffix(suff) for suff in (".yaml", ".yml")]

        for file in yaml_files:
            if file.exists():
                return file

    def generate_module(self, yaml_file: Path, output_file: Path):
        generator = PydanticGenerator(yaml_file, metadata_mode=MetadataMode.EXCEPT_CHILDREN, pydantic_version=2)
        serialized = generator.serialize()
        with open(output_file, "w") as ofile:
            ofile.write(serialized)

    def _pycache(self, path) -> Path:
        pycache = Path(path[0]) / "__pycache__"
        pycache.mkdir(parents=True, exist_ok=True)
        return pycache

    def _hash_file(self, path) -> Path:
        return self._pycache(path) / "hashes.json"

    def _python_file(self, fullname, path: Sequence[str]) -> Path:
        pycache = self._pycache(path)
        file = (pycache / fullname.split(".")[-1]).with_suffix(".py")
        return file

    def _hashes(self, hash_file: Path) -> {}:
        if hash_file.exists():
            with open(hash_file, "r") as hfile:
                hashes = json.load(hfile)
        else:
            hashes = {}
        return hashes

    def _set_module_hashes(self, hash_file: Path, module_hashes: dict, fullname: str):
        hashes = self._hashes(hash_file)
        if fullname not in hashes:
            hashes[fullname] = module_hashes
        else:
            hashes[fullname].update(module_hashes)

        with open(hash_file, "w") as hfile:
            json.dump(hashes, hfile)

    def _generate_hash(self, yaml_file: Path, output_file: Path) -> dict:
        module_hash = {"python": file_digest(output_file), "linkml": file_digest(yaml_file)}
        return module_hash

    def _update_hash(self, yaml_file: Path, output_file: Path, hash_file: Path, fullname: str):
        module_hash = self._generate_hash(yaml_file, output_file)
        self._set_module_hashes(hash_file, module_hash, fullname)


def file_digest(file: Path, method=hashlib.blake2b, buffer_size: int = 2**16) -> str:
    """
    hashlib.file_digest is >=3.11, so we make our own.

    Hash and return a b64 digest

    Thanks to https://stackoverflow.com/a/44873382
    """

    b = bytearray(buffer_size)
    mv = memoryview(b)
    digest = method()

    with open(file, "rb", buffering=0) as f:
        while chunk := f.readinto(mv):
            digest.update(mv[:chunk])
    hash = digest.hexdigest()
    return ":".join([method.__name__, hash])


def install_importer():
    pathfinder = SchemaFinder()
    sys.meta_path.append(pathfinder)
