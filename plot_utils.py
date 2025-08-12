import io, base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def png_base64_under_limit(fig, max_bytes=100_000, start_dpi=110):
    for dpi in [start_dpi, 100, 90, 80, 70, 60, 50]:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1,
                    metadata={"Software": "matplotlib"})
        data = buf.getvalue()
        if len(data) <= max_bytes:
            plt.close(fig)
            return base64.b64encode(data).decode("ascii")
    plt.close(fig)
    return base64.b64encode(data).decode("ascii")
