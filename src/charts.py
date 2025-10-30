import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

def line_chart(x, y, title=""):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y, linewidth=2)

    ax.set_title(title, fontsize=14, pad=10)
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Value", fontsize=12)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate(rotation=45)

    y_min, y_max = min(y), max(y)
    y_range = abs(y_max - y_min)

    if y_range < 10:
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.4f"))
    elif y_max < 1:
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.6f"))
    elif y_max < 1000:
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
    else:
        def human_yaxis(x, pos):
            if x >= 1e9:
                return f"{x/1e9:.2f}B"
            elif x >= 1e6:
                return f"{x/1e6:.2f}M"
            elif x >= 1e3:
                return f"{x/1e3:.2f}K"
            else:
                return f"{x:.2f}"
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(human_yaxis))

    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    return fig

