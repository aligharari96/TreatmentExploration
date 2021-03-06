from scipy import optimize

def f(z):
    return z[0] - z[1] - z[2]

cons = (
    {'type': 'ineq', 'fun': lambda z: -z[0]+z[1]+z[2]},
    {'type': 'ineq', 'fun': lambda z: z[0]-2*z[1]+z[2]},
    {'type': 'ineq', 'fun': lambda z: z[0]},
    {'type': 'ineq', 'fun': lambda z: z[1]},
    {'type': 'ineq', 'fun': lambda z: z[2]},
    {'type': 'ineq', 'fun': lambda z: 2*z[0]-z[1]-2*z[2]},
    {'type': 'eq', 'fun': lambda z: z[0]+z[1]+z[2]-1}
)
z0 = [0.45, 0.25, 0.3]
res = optimize.minimize(f, z0, constraints=cons)
print(res)

