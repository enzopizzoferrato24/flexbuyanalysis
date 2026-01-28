import numpy as np
import plotly.graph_objects as go

# --- Inputs ---
principal = 35000  
total_term = 66
step_month = 37    
decrement = 0.18   # 15% or 0.18 for 18%
rates = np.linspace(0.001, 0.20, 200) # 2% to 12% APR
months = np.arange(1, total_term + 1)

def calculate_flexbuy_surface(P, term, step, dec, rate_range):
    Z_bal = np.zeros((len(rate_range), len(months)))
    Z_princ = np.zeros((len(rate_range), len(months)))
    Z_int = np.zeros((len(rate_range), len(months)))
    
    for i, annual_rate in enumerate(rate_range):
        r = annual_rate / 12
        pmt_std = P * (r * (1 + r)**term) / ((1 + r)**term - 1)
        pmt_1 = pmt_std * (1 - dec)
        
        current_balance = P
        cum_i = 0
        cum_p = 0
        pmt = pmt_1
        
        for m in range(1, term + 1):
            if m == step:
                remaining_months = term - step + 1
                pmt = current_balance * (r * (1 + r)**remaining_months) / ((1 + r)**remaining_months - 1)
            
            interest_step = current_balance * r
            principal_step = pmt - interest_step
            current_balance -= principal_step
            cum_i += interest_step
            cum_p += principal_step
            
            Z_bal[i, m-1] = max(current_balance, 0)
            Z_int[i, m-1] = cum_i
            Z_princ[i, m-1] = cum_p
            
    return Z_bal, Z_princ, Z_int

Z_bal, Z_princ, Z_int = calculate_flexbuy_surface(principal, total_term, step_month, decrement, rates)
X, Y = np.meshgrid(months, rates)

# --- Plotting with Sensitivity Fixes ---
fig = go.Figure()

# Helper function to create the sensitive surface style
def add_sensitive_surface(z_data, name, colorscale, visible=False):
    fig.add_trace(go.Surface(
        z=z_data, x=X, y=Y, name=name,
        colorscale=colorscale,
        showscale=True,
        visible=visible,
        contours_z=dict(
            show=True,
            usecolormap=True,
            highlightcolor="white",
            project=dict(z=True), # Corrected projection syntax
            size=2000             # Corrected: 'size' defines the step interval
        )
    ))

# Add the three surfaces
add_sensitive_surface(Z_bal, 'Remaining Balance', 'Turbo', visible=True)
add_sensitive_surface(Z_int, 'Cum. Interest', 'Reds', visible=False)
add_sensitive_surface(Z_princ, 'Cum. Principal', 'Greens', visible=False)

# Layout and Buttons
fig.update_layout(
    title=f'FlexBuy 66-Month Sensitivity ({int(decrement*100)}% Decrement)',
    scene=dict(
        xaxis_title='Month',
        yaxis_title='Interest Rate (APR)',
        zaxis_title='Amount ($)',
        aspectmode='manual',
        aspectratio=dict(x=1, y=1, z=0.7) # Flattens the box for better viewing
    ),
    updatemenus=[dict(
        type="buttons",
        direction="left",
        x=0.1, y=1.15,
        buttons=[
            dict(label="Balance", method="update", args=[{"visible": [True, False, False]}]),
            dict(label="Interest", method="update", args=[{"visible": [False, True, False]}]),
            dict(label="Principal", method="update", args=[{"visible": [False, False, True]}])
        ]
    )]
)

fig.show()
