import global_configuration as global_c
import show 
import channel
import math

import gym
from gym import spaces
import numpy as np

# assume static environment 
my_ue_list = []
my_ap_list = []
VLC_LOS_matrix = [[0]*global_c.UE_num for i in range(global_c.VLC_AP_num)] # VLC_AP_num x UE_num
VLC_SINR_matrix = [[0]*global_c.UE_num for i in range(global_c.VLC_AP_num)] # VLC_AP_num x UE_num
VLC_data_rate_matrix = [[0]*global_c.UE_num for i in range(global_c.VLC_AP_num)] # VLC_AP_num x UE_num
RF_channel_gain_vector = [0 for i in range(global_c.UE_num)] # 1 x UE_num
RF_SINR_vector = [0 for i in range(global_c.UE_num)] # 1 x UE_num
RF_data_rate_vecotr = [0 for i in range(global_c.UE_num)] # 1 x UE_num


class LAHLWNenv(gym.Env):
    def __init__(self):
        super(LAHLWNenv,self).__init__()
        self.currstep = 1 # current step (index)
        self.action_space = spaces.Discrete(10) # 10 possible APS
        self.observation_space = spaces.Box(low = 0 , high = 1e10,shape=(global_c.UE_num,4),dtype=np.float32)
    
    def naxt_observation(self):
        pass


class User:
    def __init__(self,node_ID):
        self.node_ID = node_ID
        self.x_pos = np.random.uniform(-global_c.room_size/2,global_c.room_size/2)
        self.y_pos = np.random.uniform(-global_c.room_size/2,global_c.room_size/2)
        self.z_pos = 0
        self.require_data_rate = np.random.poisson(lam=70, size=None)
        self.polar_angle = 0
        self.azimuth_angle = 0
        self.prev_associated_AP = -1
        self.curr_associated_AP = -1
    
    def randomOrientationAngle(self):
        new_polor_angle = global_c.c_0 + global_c.c_1 + self.polar_angle + np.random.normal() # in degree
        self.polar_angle = new_polor_angle / 180 * math.pi
        self.azimuth_angle = -1 * math.pi


class AP:
    def __init__(self,node_ID,x_pos,y_pos,z_pos):
        self.node_ID = node_ID
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos
        


# init UE & AP
for i in range(global_c.UE_num):
    my_ue_list.append(User(i))
for j in range(global_c.RF_AP_num + global_c.VLC_AP_num):
    if j < global_c.RF_AP_num :
        my_ap_list.append(AP(j,0,0,global_c.RF_AP_height))
    else:
        delta = global_c.room_size / global_c.VLC_AP_per_row
        x = ((j-1) % global_c.VLC_AP_per_row + 1) * delta - (global_c.room_size / 2 + (global_c.room_size / global_c.VLC_AP_per_row) / 2)
        y = ((j-1) // global_c.VLC_AP_per_row + 1) * delta - (global_c.room_size / 2 + (global_c.room_size / global_c.VLC_AP_per_row) / 2)
        my_ap_list.append(AP(j,x,y,global_c.VLC_AP_height))


show.Show.printRFAPPosition(ap_list=my_ap_list)
show.Show.printVLCAPPosition(ap_list=my_ap_list)
show.Show.printUEPosition(ue_list=my_ue_list)
channel.Channel.precalculation(my_ap_list=my_ap_list,my_ue_list=my_ue_list,VLC_LOS_matrix=VLC_LOS_matrix,VLC_SINR_matrix=VLC_SINR_matrix,VLC_data_rate_matrix=VLC_data_rate_matrix,RF_channel_gain_vector=RF_channel_gain_vector,RF_SINR_vector=RF_SINR_vector,RF_data_rate_vector=RF_data_rate_vecotr)