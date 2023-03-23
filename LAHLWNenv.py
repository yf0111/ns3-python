import global_configuration as global_c
import show 
import math

import gym
from gym import spaces
import numpy as np

# assume static environment 
my_ue_list = []
ap_list = []
VLC_LOS_matrix = [[0]*global_c.UE_num for i in range(global_c.VLC_AP_num)] # VLC_AP_num x UE_num

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
        self.polar_angle = new_polor_angle
        self.azimuth_angle = -1 * global_c.PI


class AP:
    def __init__(self,node_ID,x_pos,y_pos,z_pos):
        self.node_ID = node_ID
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos

class Channel:
    def __init__(self):
        pass
    
    @staticmethod
    def getCosineOfIncidenceAngle(ue,ap):
        polar_angle = ue.polar_angle
        azimuth_angle = ue.azimuth_angle
        dx = ap.x_pos - ue.x_pos
        dy = ap.y_pos - ue.y_pos
        dz = ap.z_pos - ue.z_pos
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        first_term = dx * math.sin(polar_angle) * math.cos(azimuth_angle)
        second_term = dy * math.sin(polar_angle) * math.sin(azimuth_angle)
        last_term = dz * math.cos(polar_angle)
        return (first_term + second_term + last_term) / dist
    
    @staticmethod
    def getIrradianceAngle(ue,ap):
        dx = ap.x_pos - ue.x_pos
        dy = ap.y_pos - ue.y_pos
        plane_dist = math.sqrt(dx*dx + dy*dy)
        height_diff = ap.z_pos - ue.z_pos
        return math.atan(plane_dist / height_diff)
    
    @staticmethod
    def getDistance(ue,ap):
        dx = ap.x_pos - ue.x_pos
        dy = ap.y_pos - ue.y_pos
        dz = ap.z_pos - ue.z_pos
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    @staticmethod
    def estimateOneVlcLightOfSight(ue,ap):
        cosine_incidence_angle = Channel.getCosineOfIncidenceAngle(ue,ap)
        if Channel.radianDegree(math.acos(cosine_incidence_angle)) > global_c.field_of_view / 2 :
            return 0.0
        irradiance_angle = Channel.getIrradianceAngle(ue=ue,ap=ap)
        distance = Channel.getDistance(ue=ue,ap=ap)
        los = (global_c.lambertian_coefficient + 1) * global_c.receiver_area / (2 * global_c.PI * math.pow(distance,2))
        los = los * math.pow(math.cos(irradiance_angle),global_c.lambertian_coefficient)
        los = los * cosine_incidence_angle
        los = los * global_c.concentrator_gain
        los = los * global_c.filter_gain
        return los

    @staticmethod
    def calculateAllVlcLightOfSight(my_ue_list,VLC_LOS_matrix):
        for i in range (global_c.UE_num):
            my_ue_list[i].randomOrientationAngle()
        for AP_index in range(global_c.VLC_AP_num):   
            for UE_index in range (global_c.UE_num):
                VLC_LOS_matrix[AP_index][UE_index] = Channel.estimateOneVlcLightOfSight(my_ue_list[UE_index],ap_list[AP_index])
    
    @staticmethod
    def radianDegree(radian):
        return radian * 180.0 / global_c.PI
        


# init UE & AP
for i in range(global_c.UE_num):
    my_ue_list.append(User(i))
for j in range(global_c.RF_AP_num + global_c.VLC_AP_num):
    if j < global_c.RF_AP_num :
        ap_list.append(AP(j,0,0,global_c.RF_AP_height))
    else:
        delta = global_c.room_size / global_c.VLC_AP_per_row
        x = ((j-1) % global_c.VLC_AP_per_row + 1) * delta - (global_c.room_size / 2 + (global_c.room_size / global_c.VLC_AP_per_row) / 2)
        y = ((j-1) // global_c.VLC_AP_per_row + 1) * delta - (global_c.room_size / 2 + (global_c.room_size / global_c.VLC_AP_per_row) / 2)
        ap_list.append(AP(j,x,y,global_c.VLC_AP_height))



Channel.calculateAllVlcLightOfSight(my_ue_list=my_ue_list,VLC_LOS_matrix=VLC_LOS_matrix)
show.Show.printVLCLOS(VLC_LOS_matrix)