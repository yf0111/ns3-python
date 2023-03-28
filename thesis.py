import global_configuration as global_c
import show 
import channel
import math
import LAHLWNenv
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
all_SINR_matrix = [[0]*global_c.UE_num for i in range(global_c.RF_AP_num + global_c.VLC_AP_num)] # (RF_AP_num + VLC_AP_num) x UE_num
# ap_assocoated_matrix = [[0]*global_c.UE_num for i in range(global_c.RF_AP_num + global_c.VLC_AP_num)] # (RF_AP_num + VLC_AP_num) x UE_num
# ap_load_vector = [0 for i in range(global_c.RF_AP_num + global_c.VLC_AP_num)] # 1 x (RF_AP_num + VLC_AP_num)


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
    def createState(action):  # UE_num x 4, entry is [Wifi SNR] [highest VLC SINR] [second VLC SINR] [associated AP]
        state = [[-1]*4 for i in range(global_c.UE_num)] # UE_num
        for i in range(global_c.UE_num):
            highest_AP_value = -1
            second_AP_value = -1
            for VLC_AP_index in range(global_c.VLC_AP_num):
                if VLC_SINR_matrix[VLC_AP_index][i] > highest_AP_value:
                    second_AP_value = highest_AP_value
                    highest_AP_value = VLC_SINR_matrix[VLC_AP_index][i] 
            state[i][0] = all_SINR_matrix[0][i] # RF SINR
            state[i][1] = 0.0 if highest_AP_value < 0 else highest_AP_value # highest VLC SINR
            state[i][2] = 0.0 if second_AP_value < 0 else second_AP_value # second VLC SINR
            state[i][3] = action[i]
        return state
    
    @staticmethod
    def updateAPload(state):
        ap_load_vector = [0 for i in range(global_c.RF_AP_num + global_c.VLC_AP_num)] # 1 x (RF_AP_num + VLC_AP_num)
        for i in range(global_c.UE_num):
            if state[i][3] != -1 and state[i][3] < 5:
                ap_load_vector[state[i][3]] += 1
            if state[i][3] > 4 and state[i][3] < 9:
                ap_load_vector[0] += 1
                ap_load_vector[state[i][3]-4] += 1
        return ap_load_vector

    @staticmethod
    def calculateR1(state,prestate):
        total_throughput = 0.0
        ap_load_vector = Thesis.updateAPload(state)
        for i in range(global_c.UE_num):
            throughput = 0.0
            if my_ue_list[i].group == "SAP":
                if state[i][3] != -1 :
                    data_rate = 0.0
                    if state[i][3] < 5:
                        data_rate = RF_data_rate_vecotr[i] if state[i][3] == 0 else VLC_data_rate_matrix[state[i][3]-1][i]
                    else:
                        print("SAP UE APS is wrong!")
                    
                    eta = 0.0
                    if prestate[i][3] == state[i][3] :
                        eta = 1
                    elif prestate[i][3] != 0 and state[i][3] !=0 :
                        eta = global_c.eta_hho
                    elif prestate[i][3] == 0 and state[i][3] !=0 :
                        eta = global_c.eta_vho
                    throughput = eta * data_rate * (1 / ap_load_vector[state[i][3]])
            if my_ue_list[i].group == "LA":
                if state[i][3] != -1:
                    eta = 0.0
                    if prestate[i][3] == state[i][3]:
                        eta = 1
                    elif prestate[i][3] > 4 and state[i][3] > 4:
                        eta = global_c.eta_hho
                    else:
                        eta = global_c.eta_vho
                    if state[i][3] > 4:
                        throughput = eta * ((RF_data_rate_vecotr[i] * (1 / ap_load_vector[0])) + VLC_data_rate_matrix[state[i][3]-5][i] * (1 / ap_load_vector[state[i][3]-4]) )
                    else :
                        throughput = eta * RF_data_rate_vecotr[i] * (1 / ap_load_vector[0]) if state[i][3] == 0 else eta * VLC_data_rate_matrix[state[i][3]-1][i] * (1 / ap_load_vector[state[i][3]])
            total_throughput += throughput
        return total_throughput / global_c.UE_num


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
        print(np.matrix(ap_assocoated_matrix))
        return ap_assocoated_matrix

    