import subprocess
import re
import time

from pynvml import (nvmlInit, nvmlShutdown, nvmlDeviceGetHandleByIndex, nvmlDeviceGetClockInfo, NVML_CLOCK_SM, nvmlDeviceSetGpuLockedClocks, nvmlDeviceResetGpuLockedClocks, nvmlDeviceGetCount)

class NvmlClockReader:
    def __init__(self, gpuids):
        self.cooldown = None # seconds
        self.gpuids = [int(g) for g in gpuids]
        self.handles = {g: nvmlDeviceGetHandleByIndex(g) for g in self.gpuids}

    def get_sm_clocks(self, gpuids):
        return [int(nvmlDeviceGetClockInfo(self.handles[g], NVML_CLOCK_SM)) for g in gpuids]

    def set_sm_clock_single(self, gpuid, frequency):
        handle = self.handles[int(gpuid)]
        nvmlDeviceSetGpuLockedClocks(handle, int(frequency), int(frequency))

    def set_sm_clocks(self, gpuids, frequencies):
        for gpu, freq in zip(gpuids, frequencies):
            self.set_sm_clock_single(gpu, freq)
    
    def reset_lock_single(self, gpuid):
        handle = self.handles[int(gpuid)]
        nvmlDeviceResetGpuLockedClocks(handle)
    
    def reset_locks(self, gpuids):
        for gpuid in gpuids:
            self.reset_lock_single(gpuid)

    def close(self):
        nvmlShutdown()

    def __del__(self):
        return self.close()

nvmlInit()
DEVICES = nvmlDeviceGetCount()
the_device_ids = [i for i in range(DEVICES)]
print("Device IDS Detected: ", the_device_ids)
reader = NvmlClockReader(the_device_ids)

def set_cooldown(cooldown):
    reader.cooldown = cooldown

def set_gpu_clocks(gpuids, desired_clocks):
    reader.set_sm_clocks(gpuids, desired_clocks)


def get_gpu_clocks(gpuids):
    "accepts tuples of gpu ids, returns the clock frequencies"
    out = reader.get_sm_clocks(gpuids)

    return out

def await_gpu_clocks_stabilized(gpuids, desired_clocks):
    "returns the time it took to reach target frequencies"
    start_time = time.perf_counter()
    MAX_TIMEOUT_SECONDS = 20
    COOLDOWN = reader.cooldown
    assert COOLDOWN is not None
    time_taken = {gpuid: -1 for gpuid in gpuids}

    while (time.perf_counter() - start_time) < MAX_TIMEOUT_SECONDS:
        if -1 not in time_taken.values():
            return time_taken
        clock_times = get_gpu_clocks(gpuids)
        capture_time = time.perf_counter() - start_time
        for (gpuid, desired_clock, actual_clock) in zip(gpuids, desired_clocks, clock_times):
            if time_taken[gpuid] != -1:
                continue
            if actual_clock == desired_clock:
                time_taken[gpuid] = capture_time
        time.sleep(COOLDOWN)
    
    print(time_taken)

    for (gpuid, desired_clock) in zip(gpuids, desired_clocks):
        print(f"Wanted {desired_clock}, Actual Clock of {gpuid}: {get_gpu_clocks([gpuid])}")
    assert False and f"GPU clocks did not converge in {MAX_TIMEOUT_SECONDS} seconds"

def set_gpu_clock_and_await_stabilization(gpuids, desired_clocks):
    set_gpu_clocks(gpuids, desired_clocks)
    times= await_gpu_clocks_stabilized(gpuids, desired_clocks)
    (__name__ == "__main__") and print(times)
    return times

def reset_clocks():
    reader.reset_locks(the_device_ids)

if __name__ == "__main__":



    reset_clocks()
    # time.sleep(4)

    set_gpu_clock_and_await_stabilization(the_device_ids, [1455]*len(the_device_ids))
    set_gpu_clock_and_await_stabilization(the_device_ids, [1455]*len(the_device_ids))
    set_gpu_clock_and_await_stabilization(the_device_ids, [1455]*len(the_device_ids))
    set_gpu_clock_and_await_stabilization(the_device_ids, [1425]*len(the_device_ids))

    reset_clocks()
        
