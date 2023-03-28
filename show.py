import global_configuration as global_c

class Show:
    def __init__(self):
        pass
    
    @staticmethod
    def printVLCLOS(vlc_los_matrix):
        print("VLC LOS matrix as below : \n")
        for VLC_AP_index in range(global_c.VLC_AP_num):
            print("for VLC AP ",VLC_AP_index)
            for UE_index in range(global_c.UE_num):
                print("UE ",UE_index," : ",vlc_los_matrix[VLC_AP_index][UE_index])

    @staticmethod
    def printVLCSINR(vlc_sinr_matrix):
        print("VLC SINR matrix as below : \n")
        for VLC_AP_index in range(global_c.VLC_AP_num):
            print("for VLC AP ",VLC_AP_index)
            for UE_index in range(global_c.UE_num):
                print("UE ",UE_index," : ",vlc_sinr_matrix[VLC_AP_index][UE_index])

    @staticmethod
    def printVLCDataRate(vlc_data_rate_matrix):
        print("VLC data rate matrix as below : \n")
        for VLC_AP_index in range(global_c.VLC_AP_num):
            print("for VLC AP ",VLC_AP_index)
            for UE_index in range(global_c.UE_num):
                print("UE ",UE_index," : ",vlc_data_rate_matrix[VLC_AP_index][UE_index])

    @staticmethod
    def printRFChannelGain(RF_channel_gain_vector):
        print("RF Channel Gain vector as below : \n")
        for UE_index in range(global_c.UE_num):
            print("UE ",UE_index," : ",RF_channel_gain_vector[UE_index])

    @staticmethod
    def printRFSINR(RF_sinr_vector):
        print("RF SINR vector as below : \n")
        for UE_index in range(global_c.UE_num):
            print("UE ",UE_index," : ",RF_sinr_vector[UE_index])

    @staticmethod
    def printRFDateRate(RF_data_rate_vector):
        print("RF data rate vector as below : \n")
        for UE_index in range(global_c.UE_num):
            print("UE ",UE_index," : ",RF_data_rate_vector[UE_index])

    @staticmethod
    def printRFAPPosition(ap_list):
        for AP_index in range(global_c.RF_AP_num):
            print("Position of RF AP : (",ap_list[AP_index].x_pos,",",ap_list[AP_index].y_pos,",",ap_list[AP_index].z_pos,")")
    
    @staticmethod
    def printVLCAPPosition(ap_list):
        for AP_index in range(global_c.RF_AP_num,global_c.VLC_AP_num+1):
            print("Position of VLC AP ",AP_index," : (",ap_list[AP_index].x_pos,",",ap_list[AP_index].y_pos,",",ap_list[AP_index].z_pos,")")
        
    @staticmethod
    def printUEPosition(ue_list):
        for UE_index in range(global_c.UE_num):
            print("Position of UE ",UE_index," : (",ue_list[UE_index].x_pos,",",ue_list[UE_index].y_pos,",",ue_list[UE_index].z_pos,")")