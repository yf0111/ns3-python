import global_configuration as global_c
import show 
import channel
import math
import LAHLWNenv
import numpy as np
from pymobility.models.mobility import random_waypoint


# assume static environment 
my_ue_list = []
my_ap_list = []
VLC_LOS_matrix = [[0]*global_c.UE_num for i in range(global_c.VLC_AP_num)] # VLC_AP_num x UE_num
VLC_SINR_matrix = [[0]*global_c.UE_num for i in range(global_c.VLC_AP_num)] # VLC_AP_num x UE_num
VLC_data_rate_matrix = [[0]*global_c.UE_num for i in range(global_c.VLC_AP_num)] # VLC_AP_num x UE_num
RF_channel_gain_vector = [0 for i in range(global_c.UE_num)] # 1 x UE_num
RF_SINR_vector = [0 for i in range(global_c.UE_num)] # 1 x UE_num
RF_data_rate_vecotr = [0 for i in range(global_c.UE_num)] # 1 x UE_num
all_SINR_matrix = [[0]*global_c.UE_num for i in range(global_c.RF_AP_num + global_c.VLC_AP_num)] # (RF_AP_num + VLC_AP_num) x UE_num
rw = random_waypoint(global_c.UE_num, dimensions=(5, 5), velocity=(0.1, 1.0), wt_max=10.0)


class User:
    def __init__(self,node_ID,group):
        self.node_ID = node_ID
        self.x_pos = np.random.uniform(-global_c.room_size/2,global_c.room_size/2)
        self.y_pos = np.random.uniform(-global_c.room_size/2,global_c.room_size/2)
        self.z_pos = global_c.UE_height
        self.require_data_rate = np.random.poisson(lam=70, size=None)
        self.polar_angle = 0
        self.azimuth_angle = 0
        self.prev_associated_AP = -1
        self.curr_associated_AP = -1
        self.group = group
    
    def randomOrientationAngle(self):
        new_polor_angle = global_c.c_0 + global_c.c_1 + self.polar_angle + np.random.normal() # in degree
        self.polar_angle = new_polor_angle / 180 * math.pi
        self.azimuth_angle = -1 * math.pi

    @staticmethod
    def orwp():
        positions = next(rw)
        for i in range(global_c.UE_num):
            my_ue_list[i].x_pos = positions[i][0]
            my_ue_list[i].y_pos = positions[i][1]
            my_ue_list[i].randomOrientationAngle()


class AP:
    def __init__(self,node_ID,x_pos,y_pos,z_pos):
        self.node_ID = node_ID
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos


class Thesis:
    @staticmethod
    def init():
        # init UE & AP
        my_ue_list.clear()
        my_ap_list.clear()
        for i in range(global_c.UE_num):
            if i < global_c.LA_UE_num:
                my_ue_list.append(User(i,"LA"))
            else:
                my_ue_list.append(User(i,"SAP"))
        for j in range(global_c.RF_AP_num + global_c.VLC_AP_num):
            if j < global_c.RF_AP_num :
                my_ap_list.append(AP(j,0,0,global_c.RF_AP_height))
            else:
                delta = global_c.room_size / global_c.VLC_AP_per_row
                x = ((j-1) % global_c.VLC_AP_per_row + 1) * delta - (global_c.room_size / 2 + (global_c.room_size / global_c.VLC_AP_per_row) / 2)
                y = ((j-1) // global_c.VLC_AP_per_row + 1) * delta - (global_c.room_size / 2 + (global_c.room_size / global_c.VLC_AP_per_row) / 2)
                my_ap_list.append(AP(j,x,y,global_c.VLC_AP_height))
        
        # show.Show.printRFAPPosition(ap_list=my_ap_list)
        # show.Show.printVLCAPPosition(ap_list=my_ap_list)
        # show.Show.printUEPosition(ue_list=my_ue_list)
        channel.Channel.precalculation(my_ap_list=my_ap_list,my_ue_list=my_ue_list,VLC_LOS_matrix=VLC_LOS_matrix,VLC_SINR_matrix=VLC_SINR_matrix,VLC_data_rate_matrix=VLC_data_rate_matrix,RF_channel_gain_vector=RF_channel_gain_vector,RF_SINR_vector=RF_SINR_vector,RF_data_rate_vector=RF_data_rate_vecotr)
    
    @staticmethod
    def allSINR():
        for ap_index in range(global_c.RF_AP_num + global_c.VLC_AP_num):
            for ue_index in range(global_c.UE_num):
                if ap_index < global_c.RF_AP_num:
                    all_SINR_matrix[ap_index][ue_index] = RF_SINR_vector[ue_index]
                else:
                    all_SINR_matrix[ap_index][ue_index] = VLC_SINR_matrix[ap_index-1][ue_index]
        # print(np.matrix(all_SINR_matrix))

    @staticmethod
    def createState(action):
        # [[Wifi SNR] [highest VLC SINR] [second VLC SINR] [AP load]]  -> 一個一維大vector (1 x (UE_num + UE_num + UE_num + RF_AP_num + VLC_AP_num)) 
        wifi_snr = np.array([-1]*global_c.UE_num)
        lifi_first_snr = np.array([-1]*global_c.UE_num)
        lifi_second_snr = np.array([-1]*global_c.UE_num)
        ap_load = np.array([0]*(global_c.RF_AP_num+global_c.VLC_AP_num))
        for i in range (global_c.UE_num):
            highest_AP_value = -1
            second_AP_value = -1
            wifi_snr[i] = all_SINR_matrix[0][i] # RF SNR
            for VLC_AP_index in range(global_c.VLC_AP_num):
                if VLC_SINR_matrix[VLC_AP_index][i] > highest_AP_value:
                    second_AP_value = highest_AP_value
                    highest_AP_value = VLC_SINR_matrix[VLC_AP_index][i]
            lifi_first_snr[i] = 0.0 if highest_AP_value < 0 else highest_AP_value  # highest VLC SINR
            lifi_second_snr[i] = 0.0 if second_AP_value < 0 else second_AP_value # second VLC SINR
        for ue_index in range(global_c.UE_num):
            if action[ue_index] == 0 :
                ap_load[0] += 1 # only wifi
            elif action[ue_index] > 0 and action[ue_index] < 5:
                ap_load[action[ue_index]] += 1 # only lifi
            elif action[ue_index] > 4:
                ap_load[0] += 1
                ap_load[action[ue_index]-4] += 1
        state = np.concatenate((wifi_snr,lifi_first_snr,lifi_second_snr,ap_load))
        return state
    
    @staticmethod
    def updateAPload(state):
        #  [一個一維大vector ( wifi + lifi + lifi + ap_load) ]
        ap_load_vector = [0 for i in range(global_c.RF_AP_num + global_c.VLC_AP_num)] # 1 x (RF_AP_num + VLC_AP_num)
        for i in range(len(ap_load_vector)):
            ap_load_vector[i] = state[3*global_c.UE_num+i]
        return ap_load_vector

    @staticmethod
    def calculateR1(state,prestate,action,preaction):
        # [一個一維大vector ( wifi + lifi + lifi + ap_load) ]
        total_throughput = 0.0
        ap_load_vector = Thesis.updateAPload(state=state)
        for i in range(global_c.UE_num):
            throughput = 0.0
            if my_ue_list[i].group == "SAP":
                if action[i] != -1 :
                    data_rate = 0.0
                    if action[i] < 5:
                        data_rate = RF_data_rate_vecotr[i] if action[i] == 0 else VLC_data_rate_matrix[action[i]-1][i]
                    eta = 0.0
                    if preaction[i] == action[i]:
                        eta = 1
                    elif preaction[i] != 0 and action[i] != 0 :
                        eta = global_c.eta_hho
                    elif preaction[i] == 0 and action[i] != 0 :
                        eta = global_c.eta_vho
                    ap_allocate_time = 0.0 if ap_load_vector[action[i]] == 0 else 1 / ap_load_vector[action[i]]
                    throughput = eta * data_rate * ap_allocate_time
            if my_ue_list[i].group == "LA":
                if action[i] != -1 :
                    eta = 0.0
                    if preaction[i] == action[i]:
                        eta = 1
                    elif preaction[i] > 4 and action[i] > 4:
                        eta = global_c.eta_hho
                    else:
                        eta = global_c.eta_vho
                    rf_ap_allocate_time = 0.0 if ap_load_vector[0] == 0 else 1 / ap_load_vector[0]
                    vlc_ap_allocate_time = 0.0
                    if action[i] > 4 and ap_load_vector[action[i]-4] != 0:
                        vlc_ap_allocate_time = 1 / ap_load_vector[action[i]-4]
                    if action[i] < 5 and ap_load_vector[action[i]] != 0:
                        vlc_ap_allocate_time = 1 / ap_load_vector[action[i]]
                        
                    if action[i] > 4:
                        throughput = eta * ((RF_data_rate_vecotr[i] * rf_ap_allocate_time) + VLC_data_rate_matrix[action[i]-5][i] * vlc_ap_allocate_time)
                    else:
                        throughput = eta * RF_data_rate_vecotr[i] * rf_ap_allocate_time if action[i] == 0 else eta * VLC_data_rate_matrix[action[i]-1][i] * vlc_ap_allocate_time
            total_throughput += throughput
        return total_throughput / global_c.UE_num

    @staticmethod
    def calculateR2(state,prestate,action,preaction,ue_require):
        total_us = 0.0
        ap_load_vector = Thesis.updateAPload(state=state)
        for i in range(global_c.UE_num):
            us = 0.0
            if my_ue_list[i].group == "SAP":
                if action[i] != -1 :
                    data_rate = 0.0
                    if action[i] < 5:
                        data_rate = RF_data_rate_vecotr[i] if action[i] == 0 else VLC_data_rate_matrix[action[i]-1][i]
                    eta = 0.0
                    if preaction[i] == action[i]:
                        eta = 1
                    elif preaction[i] != 0 and action[i] != 0 :
                        eta = global_c.eta_hho
                    elif preaction[i] == 0 and action[i] != 0 :
                        eta = global_c.eta_vho
                    ap_allocate_time = 0.0 if ap_load_vector[action[i]] == 0 else 1 / ap_load_vector[action[i]]
                    throughput = eta * data_rate * ap_allocate_time
                    us = throughput / ue_require[i]
            if my_ue_list[i].group == "LA":
                if action[i] != -1 :
                    eta = 0.0
                    if preaction[i] == action[i]:
                        eta = 1
                    elif preaction[i] > 4 and action[i] > 4:
                        eta = global_c.eta_hho
                    else:
                        eta = global_c.eta_vho
                    rf_ap_allocate_time = 0.0 if ap_load_vector[0] == 0 else 1 / ap_load_vector[0]
                    vlc_ap_allocate_time = 0.0
                    if action[i] > 4 and ap_load_vector[action[i]-4] != 0:
                        vlc_ap_allocate_time = 1 / ap_load_vector[action[i]-4]
                    if action[i] < 5 and ap_load_vector[action[i]] != 0:
                        vlc_ap_allocate_time = 1 / ap_load_vector[action[i]]
                        
                    if action[i] > 4:
                        throughput = eta * ((RF_data_rate_vecotr[i] * rf_ap_allocate_time) + VLC_data_rate_matrix[action[i]-5][i] * vlc_ap_allocate_time)
                    else:
                        throughput = eta * RF_data_rate_vecotr[i] * rf_ap_allocate_time if action[i] == 0 else eta * VLC_data_rate_matrix[action[i]-1][i] * vlc_ap_allocate_time
                    us = throughput / ue_require[i]
            total_us += us * global_c.C_one
        return total_us / global_c.UE_num

    @staticmethod
    def calculateR3(state,prestate,action,preaction,ue_require):
        total_q = 0.0
        ap_load_vector = Thesis.updateAPload(state=state)
        for i in range(global_c.UE_num):
            q = 0.0
            if my_ue_list[i].group == "SAP":
                if action[i] != -1 :
                    data_rate = 0.0
                    if action[i] < 5:
                        data_rate = RF_data_rate_vecotr[i] if action[i] == 0 else VLC_data_rate_matrix[action[i]-1][i]
                    eta = 0.0
                    if preaction[i] == action[i]:
                        eta = 1
                    elif preaction[i] != 0 and action[i] != 0 :
                        eta = global_c.eta_hho
                    elif preaction[i] == 0 and action[i] != 0 :
                        eta = global_c.eta_vho
                    ap_allocate_time = 0.0 if ap_load_vector[action[i]] == 0 else 1 / ap_load_vector[action[i]]
                    throughput = eta * data_rate * ap_allocate_time
                    us = throughput / ue_require[i]
                    q = (-global_c.C_two * (1 - us)) if us <= 0.5 else global_c.C_one * us
            if my_ue_list[i].group == "LA":
                if action[i] != -1 :
                    eta = 0.0
                    if preaction[i] == action[i]:
                        eta = 1
                    elif preaction[i] > 4 and action[i] > 4:
                        eta = global_c.eta_hho
                    else:
                        eta = global_c.eta_vho
                    rf_ap_allocate_time = 0.0 if ap_load_vector[0] == 0 else 1 / ap_load_vector[0]
                    vlc_ap_allocate_time = 0.0
                    if action[i] > 4 and ap_load_vector[action[i]-4] != 0:
                        vlc_ap_allocate_time = 1 / ap_load_vector[action[i]-4]
                    if action[i] < 5 and ap_load_vector[action[i]] != 0:
                        vlc_ap_allocate_time = 1 / ap_load_vector[action[i]]
                        
                    if action[i] > 4:
                        throughput = eta * ((RF_data_rate_vecotr[i] * rf_ap_allocate_time) + VLC_data_rate_matrix[action[i]-5][i] * vlc_ap_allocate_time)
                    else:
                        throughput = eta * RF_data_rate_vecotr[i] * rf_ap_allocate_time if action[i] == 0 else eta * VLC_data_rate_matrix[action[i]-1][i] * vlc_ap_allocate_time
                    us = throughput / ue_require[i]
                    q = ( -global_c.C_two * (1-us)) if us <= 0.5 else global_c.C_one * us
            total_q += q
        return total_q / global_c.UE_num

    @staticmethod
    def action_to_AP_association_matrix(action):
        ap_assocoated_matrix = [[0]*global_c.UE_num for i in range(global_c.RF_AP_num + global_c.VLC_AP_num)] # (RF_AP_num + VLC_AP_num) x UE_num
        for i in range(global_c.UE_num):
            if action[i] == 0:
                ap_assocoated_matrix[0][i] = 1
            if action[i] > 0 and action[i] < 5:
                ap_assocoated_matrix[action[i]][i] = 1
            if action[i] > 4 :
                ap_assocoated_matrix[0][i] = 1
                ap_assocoated_matrix[action[i]-4][i] = 1
        return ap_assocoated_matrix

    @staticmethod
    def getUEdemand():
        ue_demand = [] 
        for i in range(global_c.UE_num):
            ue_demand.append(my_ue_list[i].require_data_rate)
        return ue_demand
    
    @staticmethod
    def cal_final_data_rate(action):
        ue_final = []
        for i in range(global_c.UE_num):
            if action[i] == 0:
                ue_final.append(RF_data_rate_vecotr[i])
            elif action[i] > 0 and action[i] < 5 :
                ue_final.append(VLC_data_rate_matrix[action[i]-1][i])
            elif action[i] > 4 :
                ue_final.append(RF_data_rate_vecotr[i] + VLC_data_rate_matrix[action[i]-5][i])
        return ue_final
    
    @staticmethod
    def cal_performance(ue_new_satisfaction,ue_old_satisfaction,ue_get,ue_require):
        
        # reliability
        ue_reliability = [0 for i in range(global_c.UE_num)]  # 1 x UE_num
        for ue_index in range(global_c.UE_num):
            for ap_index in range(global_c.RF_AP_num+global_c.VLC_AP_num):
                if ap_index < global_c.RF_AP_num:
                    if RF_SINR_vector[ue_index] > global_c.SINR_threshold:
                        ue_reliability[ue_index] = 1
                    else:
                        ue_reliability[ue_index] = 0
                else:
                    if VLC_SINR_matrix[ap_index-1][ue_index] > global_c.SINR_threshold:
                        ue_reliability[ue_index] = 1
                    else:
                        ue_reliability[ue_index] = 0

        # latency
        ue_latency = [0 for i in range(global_c.UE_num)]  # 1 x UE_num
        for ue_index in range(global_c.UE_num):
            TL = 0.4 + (global_c.packet_size / ( 1e6 * ue_get[ue_index]) * 1e3)
            if TL < global_c.T_max:
                ue_latency[ue_index] = 1
            else:
                ue_latency[ue_index] = 0
        
        # data rate
        ue_data_rate = [0 for i in range(global_c.UE_num)]  # 1 x UE_num
        for ue_index in range(global_c.UE_num):
            ue_data_rate[ue_index] = min(ue_get[ue_index] / ue_require[ue_index],1)
        
        # new satisfaction
        for ue_index in range(global_c.UE_num):
            if ue_get[ue_index] < ue_require[ue_index]:
                ue_new_satisfaction[ue_index] = 0
            else:
                if ue_index < (global_c.UE_num / 2):
                    ue_new_satisfaction[ue_index] = (0.4 * ue_reliability[ue_index]) + (0.4 * ue_latency[ue_index]) + (0.2 * ue_data_rate[ue_index])
                else:
                    ue_new_satisfaction[ue_index] = (0.1 * ue_reliability[ue_index]) + (0.1 * ue_latency[ue_index]) + (0.8 * ue_data_rate[ue_index])

        # old satisfaction
        for ue_index in range(global_c.UE_num):
            ue_old_satisfaction[ue_index] = min(ue_get[ue_index] / ue_require[ue_index] , 1)
           