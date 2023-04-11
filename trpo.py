import global_configuration as global_c
import numpy as np
from LAHLWNenv import LAHLWNenv
import thesis
from sb3_contrib import TRPO
import csv
import time


start = time.time()
ue_satisfaction = [[0] for i in range(global_c.UE_num)]
avg_satis = [[0] for i in range(global_c.state_num)]
avg_throughput = [[0] for i in range(global_c.state_num)]
env = LAHLWNenv()

# # --------------------------------- training model ---------------------------------
model = TRPO(policy="MlpPolicy",env=env,verbose=1,gamma=0.9,target_kl=0.01)
model.learn(total_timesteps=10000000)
model.get_parameters()
model.save("trpo_LAHLWN")
del model
# # --------------------------------- end of training model ---------------------------

model = TRPO.load("trpo_LAHLWN")


for one in range(global_c.state_num):
    obs = env.reset()
    ue_require = thesis.Thesis.getUEdemand()
    print("require:",*ue_require)
    action, _states = model.predict(obs, deterministic=True)
    print(action)
    # obs, reward, done, info = env.step(action)
    ue_get = thesis.Thesis.cal_final_data_rate(action=action)
    print("get:",*ue_get,"\n")
    total_satis = 0.0
    total_throughput = 0.0
    effi_num = 0
    for i in range(global_c.UE_num):
        ue_satisfaction[i] = min(ue_get[i] / ue_require[i],1)
        # total_satis += ue_satisfaction[i]
        # total_throughput += ue_get[i]
        if ue_get[i] != 0: # if this ue get is not 0 -> can cal in efficient ue
            total_throughput += ue_get[i]
            total_satis += ue_satisfaction[i]
            effi_num += 1
    # avg_satis[one] = total_satis / global_c.UE_num
    # avg_throughput[one] = total_throughput / global_c.UE_num
    
    avg_satis[one] = total_satis / effi_num if effi_num != 0 else 0
    avg_throughput[one] = total_throughput / effi_num if effi_num != 0 else 0



with open('output.csv','w',newline='') as csvfile:
    writer = csv.writer(csvfile,delimiter=',')
    for i in range(global_c.state_num):
        writer.writerow([avg_satis[i],avg_throughput[i]])

print("avg satisfaction:",avg_satis)
print("avg throughput:",avg_throughput)

end = time.time()
print("執行時間：%f 秒" % (end - start))
