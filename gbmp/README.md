# GBMP
This tool is a custom compiler/processor for BMP files to binary data. It also includes a color clamper for convinence. 

### Requirements
- Python 3.9.x
- OpenCV
- NumPy
- TOML
```
pip install opencv-python numpy toml
```

## Configuration
GBMP can be configured using a TOML config file (`gbmp_config.toml`) and/or CLI arguments.

### Command-Line Arguments
| Argument                | Description                     |
| ------------------------- | ------------ |
| `-c`, `--config`          | Path to TOML config file (default: `gbmp_config.toml`) |
| `-d`, `--directory`       | Path to directory of BMP images |
| `-f`, `--file`            | Path to a single BMP image  |
| `-v`, `--verbose`         | Enable logging of INFO messages|
| `-nc`, `--no-color-clamp` | FIXME   |
| `-cc`, `--color-clamp`    | FIXME |

You can override config file options with CLI arguments. At least one of `--directory` or `--file` must be provided.


# TODO:
- Finish colorclamp.p and integrate it to gbmp.py
- Finish World/Actor tile processing
- Smart load sprite data 
- Extend config file for future uses


