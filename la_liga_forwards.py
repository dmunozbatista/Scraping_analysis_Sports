import seaborn as sns
import matplotlib.pyplot as plt
import pathlib
from clean_data import top_10_per_90, top_15_prgc


plot_1 = pathlib.Path(__file__).parents[1] / "Lamine_Yamal/initial_plot.png"
plot_per90 = pathlib.Path(__file__).parents[1] / "Lamine_Yamal/plot_per90_minutes.png"

# Plot for first analysis. Most generated expected goals and progressive carries
sns.set_style("white")

# Define the desired order for the age range categories
age_range_order = ["under 20", "20 - 25", "25 - 30", "over 30"]
first_la_liga_plot = sns.scatterplot(data=top_15_prgc, x="xg_plus_xa", y="prgc", hue="age_range", hue_order=age_range_order)
first_la_liga_plot.legend(title='Age')
first_la_liga_plot.set(xlabel="Expected goals plus expected assists", ylabel="Progressive carries")
first_la_liga_plot.text(9, 129, "Sávio")
first_la_liga_plot.text(12, 130, "Rodrygo")
first_la_liga_plot.text(10.2, 95, "Vinicius")
first_la_liga_plot.text(6.5, 91, "Greenwood")
first_la_liga_plot.text(8.2, 89, "N. Williams")
first_la_liga_plot.text(8.2, 80, "Yamal")
first_la_liga_plot.text(12, 65, "Bellingham")
sns.despine()
plt.savefig(plot_1)


sns.set_style("white")

# Define the desired order for the age range categories
age_range_order = ["under 20", "20 - 25", "25 - 30", "over 30"]
first_la_liga_plot = sns.scatterplot(data=top_10_per_90, x="xg_plus_xa_90", y="prgc_90", hue="age_range", hue_order=age_range_order)
first_la_liga_plot.legend(title='Age')
first_la_liga_plot.set(xlabel="Expected goals plus expected assists per 90 mins", ylabel="Progressive carries per 90 mins")
# first_la_liga_plot.text(9, 129, "Sávio")
first_la_liga_plot.text(0.52, 6.05, "Rodrygo")
first_la_liga_plot.text(0.66, 6, "Vinicius")
# first_la_liga_plot.text(6.5, 91, "Greenwood")
first_la_liga_plot.text(0.42, 5.05, "N. Williams")
first_la_liga_plot.text(0.52, 4.95, "Yamal")
first_la_liga_plot.text(0.61, 4.3, "Brahim")
sns.despine()
plt.savefig(plot_per90)