import numpy as np
import plotly.graph_objects as go

# --- Fixed Inputs ---
msrp = 35000
total_term = 75
step_month = 37
decrement = 0.15        # 18% FlexBuy decrement
annual_depreciation = 0.18 
rates = np.linspace(0.02, 0.12, 40) # 2% to 12% APR
months = np.arange(1, total_term + 1)
X, Y = np.meshgrid(months, rates)

# --- Slider Config ---
ltv_range = np.arange(0.80, 1.55, 0.05) # 80% to 150% in 5% steps

def calculate_equity_surface(ltv, V0, term, step, dec, rate_range, dep_rate):
    P = V0 * ltv
    Z_equity = np.zeros((len(rate_range), len(months)))
    
    for i, annual_rate in enumerate(rate_range):
        r = annual_rate / 12
        pmt_std = P * (r * (1 + r)**term) / ((1 + r)**term - 1)
        pmt_1 = pmt_std * (1 - dec)
        
        current_balance = P
        pmt = pmt_1
        
        for m in range(1, term + 1):
            if m == step:
                rem_m = term - step + 1
                pmt = current_balance * (r * (1 + r)**rem_m) / ((1 + r)**rem_m - 1)
            
            # Update balance
            interest_charge = current_balance * r
            current_balance -= (pmt - interest_charge)
            
            # Calculate Vehicle Value (Exponential Depreciation)
            current_value = V0 * (1 - dep_rate)**(m/12)
            Z_equity[i, m-1] = current_value - current_balance
            
    return Z_equity

# --- Create Figure ---
fig = go.Figure()

# Add a surface for each LTV step (only the 115% one visible by default)
for ltv in ltv_range:
    Z_eq = calculate_equity_surface(ltv, msrp, total_term, step_month, decrement, rates, annual_depreciation)
    
    is_default = (round(ltv, 2) == 1.15)
    
    fig.add_trace(go.Surface(
        z=Z_eq, x=X, y=Y,
        name=f'{int(ltv*100)}% LTV',
        visible=is_default,
        colorscale='RdYlGn',
        cmid=0,
        showscale=True,
        colorbar=dict(title="Equity ($)"),
        contours_z=dict(
            show=True, project=dict(z=True), 
            size=1000, usecolormap=True, highlightcolor="white"
        )
    ))

# Add the Month 37 "Decision Wall" 
# (Static visual reference showing where the payment jumps)
fig.add_trace(go.Scatter3d(
    x=[37, 37, 37, 37, 37], 
    y=[min(rates), max(rates), max(rates), min(rates), min(rates)], 
    z=[-15000, -15000, 10000, 10000, -15000],
    mode='lines',
    line=dict(color='black', width=4),
    name='Month 37 Jump'
))

# --- Create Slider Steps ---
steps = []
for i, ltv in enumerate(ltv_range):
    # Create a visibility list (True for the current LTV trace, False for others)
    # The last trace (the wall) is always True
    visible_list = [False] * len(ltv_range)
    visible_list[i] = True
    visible_list.append(True) 
    
    step = dict(
        method="update",
        args=[{"visible": visible_list},
              {"title": f"FlexBuy Analysis: {int(ltv*100)}% Initial LTV"}],
        label=f"{int(ltv*100)}%"
    )
    steps.append(step)

sliders = [dict(
    active=7, # Starts at 115% (the 8th element in 0.80-1.50 range)
    currentvalue={"prefix": "Initial LTV: "},
    pad={"t": 50},
    steps=steps
)]

# --- Layout ---
fig.update_layout(
    sliders=sliders,
    title=f"FlexBuy Analysis: 115% Initial LTV",
    scene=dict(
        xaxis_title='Month',
        yaxis_title='APR',
        zaxis_title='Equity ($)',
        zaxis=dict(range=[-15000, 15000]), # Keep scale constant to see the drop
        camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))
    ),
    margin=dict(l=0, r=0, b=0, t=50)
)

fig.show()

# Save as an interactive standalone file
fig.write_html("FlexBuy_Analysis.html")

