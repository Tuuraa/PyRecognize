from Models.recorder import Recorder, RecorderConfig
from config import Model_path


def main():
    recorder = Recorder(record_config=RecorderConfig(Model_path))
    recorder.run()


if __name__ == "__main__":
    main()