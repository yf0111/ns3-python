import gym
import numpy as np
from LAHLWNenv import LAHLWNenv
import thesis

from sb3_contrib import TRPO

env = LAHLWNenv()

# model = TRPO(policy="MlpPolicy",env=env,verbose=1,gamma=0.9,target_kl=0.01)
# model.learn(total_timesteps=1000000)
# model.get_parameters()
# model.save("trpo_LAHLWN")
# del model # remove to demonstrate saving and loading
model = TRPO.load("trpo_LAHLWN")
# # 是不是以上就訓練完了? -> 是
obs = env.reset()
ue_require = thesis.Thesis.getUEdemand()
print("require:",*ue_require)
action, _states = model.predict(obs, deterministic=True)
print(action)

# for i in range(1000):
#     obs = env.reset()
#     ue_require = thesis.Thesis.getUEdemand()
#     print("require:",*ue_require)
#     action, _states = model.predict(obs, deterministic=True)
#     # obs, reward, done, info = env.step(action)
#     ue_final = thesis.Thesis.cal_final_data_rate(action=action)
#     print("get:",*ue_final,"\n")






# while True:
#     action, _states = model.predict(obs, deterministic=True)
#     obs, reward, done, info = env.step(action)
#     if done:
#       obs = env.reset()
#       env.render()
