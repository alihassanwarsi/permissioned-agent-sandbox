import pytest
from app.tools.file_reader import FileReaderInput, read_files, SANDBOX_DIR

@pytest.fixture(autouse=True)
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr("app.tools.file_reader.SANDBOX_DIR", tmp_path)
    (tmp_path / "notes.txt").write_text("hello from sandbox")
    (tmp_path / "a_folder").mkdir()
    return tmp_path

def test_read_files_inside_sandbox():
    result = read_files(FileReaderInput(path="notes.txt"))
    assert result.content == "hello from sandbox"

def test_block_path_escaping_sandbox():
    with pytest.raises(PermissionError):
        read_files(FileReaderInput(path="../../test/etc"))

def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        read_files(FileReaderInput(path="ghost.txt"))

def test_directory_path_raises():
    with pytest.raises(ValueError):
        read_files(FileReaderInput(path="a_folder"))