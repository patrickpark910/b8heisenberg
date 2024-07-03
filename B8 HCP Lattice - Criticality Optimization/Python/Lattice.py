import numpy as np
import pandas as pd
M = np.array([[1,0,0],[0.5,np.sqrt(3)/2,0],[0.5,0.5/np.sqrt(3),np.sqrt(2.0/3.0)]]).T


x = np.array([[[[i,j,k] for i in range(-50,50)] for j in range(-50,50)] for k in range(-50,50)]).reshape(1000000,3)
X = np.matmul(M,x.T)
df = pd.DataFrame(X.T, columns= ['x','y','z'])
df['r'] = df.apply(lambda row : np.linalg.norm([row['x'], row['y'], 0.0]), axis = 1)
df['norm'] = df.apply(lambda row : np.linalg.norm([row['x'], row['y'], row['z']]), axis = 1)

df.to_csv('lattice.csv')