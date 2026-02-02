## Prerequistes:
- vllm must be installed
- hugging face hub must be logged into
- `pip install nvidia-ml-py`
## Running:
- Modify ./do_that_shit.sh to replace the `PYTHON=` variable with your Python environment
- Find out which frequencies are supported on the gpu
- Run `./do_that_shit.sh "test_data" 0 2325 1935 1545 1155`, for example in this case `test_data` is the prefix of the save file, `0` is the GPU ID we are testing, and `2325 1935 1545 1155` are the frequencies we are testing changes.
