import math

room_size = 8
state_num = 100
simulation_num = 1000

# RF AP
RF_AP_num = 1
RF_AP_height = 3
RF_AP_bandwidth = 20
RF_AP_power = 0.1
RF_noise_power_spectral_density = 3.98e-15

# VLC AP
VLC_AP_num = 4
VLC_AP_per_row = 2
VLC_AP_height = 3
VLC_AP_power = 3
VLC_AP_bandwidth = 40
VLC_noise_power_spectral_density = 1e-15
conversion_efficiency = 0.53


# VLC channel 
field_of_view = 60.0
PHI_half = 60.0
filter_gain = 1.0
refractive_index = 1.5
receiver_area = 1e-4
lambertian_coefficient = (-1) / (math.log2(math.cos(PHI_half / 180.0 * math.pi)))
concentrator_gain = math.pow(refractive_index, 2) / math.pow(math.sin(field_of_view / 2 / 180.0 * math.pi), 2)

# RF channel
RF_carrier_frequency = 2.4e9
breakpoint_distance = 0.05
RF_three_db_cutoff = 1


# UE
UE_num = 10
LA_UE_num = int(UE_num * 0.4)
UE_height = 1

# random orientation angle (UE random orientation)
coherence_time = 130.0
sampling_time = 13.0
angle_mean = 30.0
angle_variance = 7.78
c_1 = pow(0.05, sampling_time/coherence_time)
c_0 = (1.0 - c_1) * angle_mean
noise_variance = (1.0 - c_1 * c_1) * angle_variance * angle_variance


# system parameter
eta_hho = 0.9
eta_vho = 0.6
C_one = 100
C_two = 1000
SINR_threshold = 5
T_max = 1
packet_size = 2000
