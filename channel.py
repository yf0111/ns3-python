import global_configuration as global_c
import math
import numpy as np
import show


class Channel:
    def __init__(self):
        pass
    
    # vlc channel gain
    @staticmethod
    def radianDegree(radian):
        return radian * 180.0 / math.pi
    
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
        los = (global_c.lambertian_coefficient + 1) * global_c.receiver_area / (2 * math.pi * math.pow(distance,2))
        los = los * math.pow(math.cos(irradiance_angle),global_c.lambertian_coefficient)
        los = los * cosine_incidence_angle
        los = los * global_c.concentrator_gain
        los = los * global_c.filter_gain
        return los

    @staticmethod
    def calculateAllVlcLightOfSight(my_ue_list,VLC_LOS_matrix,my_ap_list):
        for i in range (global_c.UE_num):
            my_ue_list[i].randomOrientationAngle()
        for AP_index in range(1,global_c.RF_AP_num+global_c.VLC_AP_num):
            for UE_index in range (global_c.UE_num):
                VLC_LOS_matrix[AP_index-1][UE_index] = Channel.estimateOneVlcLightOfSight(my_ue_list[UE_index],my_ap_list[AP_index])
    
    # vlc sinr
    @staticmethod
    def calculateAllVlcSINR(VLC_LOS_matrix,VLC_SINR_matrix,my_ue_list,my_ap_list):
        for AP_index in range (global_c.VLC_AP_num):
            for UE_index in range (global_c.UE_num):
                VLC_SINR_matrix[AP_index][UE_index] = Channel.estimateOneVlcSINR(VLC_LOS_matrix=VLC_LOS_matrix,ue=UE_index,ap=AP_index)
    
    @staticmethod
    def estimateOneVlcSINR(VLC_LOS_matrix,ue,ap):
        interference = 0.0
        for AP_index in range(global_c.VLC_AP_num):
            if AP_index != ap:
                interference += math.pow(global_c.conversion_efficiency * global_c.VLC_AP_power * VLC_LOS_matrix[AP_index][ue],2)
        noise = global_c.VLC_AP_bandwidth * global_c.VLC_noise_power_spectral_density
        SINR = math.pow(global_c.conversion_efficiency * global_c.VLC_AP_power * VLC_LOS_matrix[ap][ue],2) / (interference + noise)
        return 0 if SINR == 0 else 10 * math.log10(SINR)
    
    @staticmethod
    def updateAllvlcSINR(VLC_LOS_matrix,VLC_SINR_matrix,AP_association_matrix):
        for VLC_AP_index in range(global_c.VLC_AP_num):
            for UE_index in range(global_c.UE_num):
                VLC_SINR_matrix[VLC_AP_index][UE_index] = Channel.estimateUpdateVlcSINR(VLC_LOS_matrix,VLC_AP_index,UE_index,AP_association_matrix)

    @staticmethod
    def estimateUpdateVlcSINR(VLC_LOS_matrix,VLC_AP_index,UE_index,AP_association_matrix):
        i_flag = 0
        for check in range(global_c.UE_num):
            if check != UE_index and AP_association_matrix[VLC_AP_index][check] == 1 :
                i_flag = 1
        interference = 0.0
        if i_flag == 1 :
            for AP_index in range(global_c.VLC_AP_num):
                if AP_index != VLC_AP_index:
                    interference += math.pow(global_c.conversion_efficiency * global_c.VLC_AP_power * VLC_LOS_matrix[AP_index][UE_index],2)
        noise = global_c.VLC_AP_bandwidth * global_c.VLC_noise_power_spectral_density
        SINR = math.pow(global_c.conversion_efficiency * global_c.VLC_AP_power * VLC_LOS_matrix[VLC_AP_index][UE_index],2) / (interference + noise)
        return 0 if SINR == 0 else 10 * math.log10(SINR)
    
    @staticmethod
    def calculateAllVlcDataRate(VLC_SINR_matrix,VLC_data_rate_matrix):
        for AP_index in range(global_c.VLC_AP_num):
            for UE_index in range(global_c.UE_num):
                VLC_data_rate_matrix[AP_index][UE_index] = Channel.estimateOneVlcDataRate(VLC_SINR_matrix,AP_index,UE_index)
    
    @staticmethod
    def estimateOneVlcDataRate(VLC_SINR_matrix,AP_index,UE_index):
        data_rate = (global_c.VLC_AP_bandwidth / 2) * math.log2(1 + (6 / math.pi * math.e) * VLC_SINR_matrix[AP_index][UE_index])
        return 0.0 if math.isnan(data_rate) else data_rate
    
    @staticmethod
    def calculateRFChannelGain(my_ue_list,my_ap_list,RF_channel_gain_vector):
        for i in range(global_c.UE_num):
            RF_channel_gain_vector[i] = Channel.estimateOneRFChannelGain(ap=my_ap_list[0],ue=my_ue_list[i])

    @staticmethod
    def estimateOneRFChannelGain(ap,ue):
        distance = Channel.getDistance(ap=ap,ue=ue)
        h = np.random.rayleigh(2.46)
        l_d = 20 * math.log10( distance + global_c.RF_carrier_frequency ) - 147.5 + 3
        if distance >= global_c.breakpoint_distance:
            l_d += +35 * math.log10( distance/global_c.breakpoint_distance )
        rf_loss_channel_gain = math.pow(10,(-l_d/10)) * math.pow(h,2)
        return rf_loss_channel_gain
        
    @staticmethod
    def calculateAllRFSINR(RF_SINR_vector,RF_channel_gain_vector):
        for i in range(global_c.UE_num):
            RF_SINR_vector[i] = Channel.estimateOneRFSINR(RF_channel_gain_vector=RF_channel_gain_vector,ue=i)

    @staticmethod
    def estimateOneRFSINR(RF_channel_gain_vector,ue):
        numerator = global_c.RF_AP_power * RF_channel_gain_vector[ue]
        denominator = global_c.RF_noise_power_spectral_density * global_c.RF_AP_bandwidth
        SINR = numerator / denominator
        return SINR

    @staticmethod
    def calculateALLRFDataRate(RF_data_rate_vector,RF_SINR_vector):
        for i in range(global_c.UE_num):
            RF_data_rate_vector[i] = Channel.estimateOneRFDataRate(RF_SINR_vector = RF_SINR_vector,ue=i)

    @staticmethod
    def estimateOneRFDataRate(RF_SINR_vector,ue):
        data_rate = global_c.RF_AP_bandwidth * math.log2(1+RF_SINR_vector[ue])
        return 0.0 if math.isnan(data_rate) else data_rate
    

    @staticmethod
    def precalculation(my_ap_list,my_ue_list,VLC_LOS_matrix,VLC_SINR_matrix,VLC_data_rate_matrix,RF_channel_gain_vector,RF_SINR_vector,RF_data_rate_vector):
        Channel.calculateAllVlcLightOfSight(my_ue_list=my_ue_list,my_ap_list=my_ap_list,VLC_LOS_matrix=VLC_LOS_matrix)
        Channel.calculateAllVlcSINR(VLC_LOS_matrix=VLC_LOS_matrix,VLC_SINR_matrix=VLC_SINR_matrix,my_ap_list=my_ap_list,my_ue_list=my_ue_list)
        Channel.calculateAllVlcDataRate(VLC_SINR_matrix=VLC_SINR_matrix,VLC_data_rate_matrix=VLC_data_rate_matrix)

        # show.Show.printVLCLOS(VLC_LOS_matrix)
        # show.Show.printVLCSINR(VLC_SINR_matrix)
        # show.Show.printVLCDataRate(VLC_data_rate_matrix)

        Channel.calculateRFChannelGain(my_ap_list=my_ap_list,my_ue_list=my_ue_list,RF_channel_gain_vector=RF_channel_gain_vector)
        Channel.calculateAllRFSINR(RF_SINR_vector=RF_SINR_vector,RF_channel_gain_vector=RF_channel_gain_vector)
        Channel.calculateALLRFDataRate(RF_data_rate_vector=RF_data_rate_vector,RF_SINR_vector=RF_SINR_vector)
        
        # show.Show.printRFChannelGain(RF_channel_gain_vector)
        # show.Show.printRFSINR(RF_SINR_vector)
        # show.Show.printRFDateRate(RF_data_rate_vector)

