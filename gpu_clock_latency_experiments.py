from gpu_clock_change_funcs import reader, set_gpu_clock_and_await_stabilization, reset_clocks, set_gpu_clocks, get_gpu_clocks, set_cooldown
import time
import json
import argparse
import warnings

on_rtx_6000 = [3105, 2910, 2715, 2520, 2325, 2130, 1935, 1740, 1545, 1350, 1155, 960, 765, 570, 375]
subset = [3105, 2715, 2325, 1935, 1545, 1155, 765, 375][2:]

def clock_frequency_change_experiment(cooldown, filename, frequencies_to_play_with = None, gpu_id = None):
    if frequencies_to_play_with is None:
        frequencies_to_play_with = subset
        warnings.warn(f"Caution! Using RTX 6000 Frequencies of {frequencies_to_play_with}")

    assert gpu_id is not None
    GPU_ID_WE_WANT = gpu_id
    print(f"Running on GPU {GPU_ID_WE_WANT}")
    print(f"Running with: {frequencies_to_play_with}")

    set_cooldown(cooldown)

    COUNTS = 3

    reset_clocks()
    time.sleep(10)

    clock_change_latency_logs = dict()
    print("Cooldown Time Between NVML Calls: ", cooldown)
    clock_change_latency_logs["nvml_cooldown"] = cooldown
    
    save_file = f"{filename}_cooldown{cooldown}.json"

    print("Saving Data to ", save_file)

    def fix_logs(logs):
        return  {
            f"{k[0]}_{k[1]}": v
            for k, v in logs.items()
        }

    for frequency in frequencies_to_play_with:
        for otherfrequency in frequencies_to_play_with:

            clock_change_latency_logs[(frequency, otherfrequency)] = list()

            for i in range(COUNTS):
                set_gpu_clock_and_await_stabilization(gpuids=[GPU_ID_WE_WANT], desired_clocks=[frequency])
                transition_times = set_gpu_clock_and_await_stabilization(gpuids=[GPU_ID_WE_WANT], desired_clocks=[otherfrequency])
                gpu0s = transition_times[GPU_ID_WE_WANT]
                clock_change_latency_logs[(frequency, otherfrequency)].append(gpu0s)
                reset_clocks()
            
            all = clock_change_latency_logs[(frequency, otherfrequency)]
            avg = sum(all)/len(all)


            with open(save_file, "w+") as f:
                json.dump(fix_logs(clock_change_latency_logs), f)
            
            print(f"Changing from {frequency} MHZ to {otherfrequency} MHZ took an average of {avg}, all of {all}")


# def overlapped_frequency_change_experiment():
#     times_to_change = [4, 8, 12, 16, 20, 24, 28][:len(subset)]
#     frequency_to_change_to = subset
#     start_time = time.perf_counter()

#     captured_frequency_changes = list()
#     time_stamps_for_captured = list()

#     change_times = list()
#     changed_to = list()

#     for time_change, frequency in zip(times_to_change, frequency_to_change_to):
#         print("Changing Frequency To ", frequency, "At ", (time.perf_counter() - start_time), "seconds")
#         set_gpu_clocks([GPU_ID_WE_WANT], [frequency])
#         change_times.append(time.perf_counter()-start_time)
#         changed_to.append(frequency)

#         while (time.perf_counter() - start_time) < time_change:
#             time_stamps_for_captured.append((time.perf_counter() - start_time))
#             captured_frequency_changes.append(get_gpu_clocks([GPU_ID_WE_WANT]))
#             time.sleep(1)

#     current_running = time.perf_counter() - start_time
#     track_ten_more_seconds = current_running + 100
#     while (time.perf_counter() - start_time) < track_ten_more_seconds:
#         time_stamps_for_captured.append((time.perf_counter() - start_time))
#         captured_frequency_changes.append(get_gpu_clocks([GPU_ID_WE_WANT]))
#         time.sleep(1)

#     answers = {
#         "requested_frequency_change_time_stamps": change_times,
#         "requested_frequency_changes": changed_to,
#         "captured_frequency_time_stamps": time_stamps_for_captured,
#         "captured_frequency_changes": captured_frequency_changes
#     }

#     with open("overlapped_frequency_experiment_vllm.json", "w+") as f:
#         json.dump(answers, f)

        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run clock frequency change experiment with cooldown."
    )

    parser.add_argument(
        "--cooldown",
        type=float,
        required=True,
        help="Cooldown time (in seconds) between clock frequency changes"
    )

    parser.add_argument(
        "--device",
        type=int,
        required=True,
        help="NVIDIA device number"
    )

    parser.add_argument(
        "--filename",
        type=str,
        required=True,
        help="Output filename to store experiment results"
    )

    parser.add_argument(
        "--frequencies",
        type=int,
        nargs="+",
        required=False,
        help="List of GPU clock frequencies (in MHz) to test transitions between"
    )

    args = parser.parse_args()

    clock_frequency_change_experiment(args.cooldown, args.filename, args.frequencies, args.device)