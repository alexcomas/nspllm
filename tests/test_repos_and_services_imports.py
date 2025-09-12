from repositories.implementations.mock_llm_repo import MockLLMRepository
from repositories.implementations.file_env_repo import FileEnvRepo
from services.implementations.environment_service_fs import FileSystemEnvironmentService


def test_mock_llm_echo():
    repo = MockLLMRepository()
    out = repo.chat([{"role": "user", "content": "hello"}])
    assert out == "MOCK:hello"


def test_env_service_paths(tmp_path):
    repo = FileEnvRepo()
    fs_storage = tmp_path / "storage"
    fs_temp = tmp_path / "temp"
    fs_storage.mkdir()
    fs_temp.mkdir()
    svc = FileSystemEnvironmentService(repo, str(fs_storage), str(fs_temp))

    sim_code = "sim1"
    # write meta and signals should create files
    svc.write_meta(sim_code, {"maze_name": "the_ville"})
    svc.signal_curr_sim(sim_code, 5)

    assert repo.exists(f"{fs_storage}/{sim_code}/reverie/meta.json")
    assert repo.exists(f"{fs_temp}/curr_sim_code.json")
    assert repo.exists(f"{fs_temp}/curr_step.json")
