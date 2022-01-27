import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import streamlit as st


class Schelling:
    def __init__(self, city_length, empty_ratio,
                 intolerance, n_ethnicities, seed=None):
        self.city_length = int(city_length)
        self.city_size = [self.city_length, self.city_length]
        self.empty_ratio = empty_ratio
        self.intolerance = intolerance

        self.choices = np.full(n_ethnicities+1, (1-empty_ratio)/n_ethnicities)
        self.choices[0] = empty_ratio

        self.rng = np.random.default_rng(seed)
        self.city = self.rng.choice(np.arange(n_ethnicities+1),
                                    size=self.city_size, p=self.choices)

    def similarity_ratio(self):
        mean_ratio = 0
        count = 0
        for (row, col), value in np.ndenumerate(self.city):
            if value != 0:
                neighborhood = np.roll(self.city, (1-row, 1-col),
                                       axis=(0, 1))[:3, :3]
                n_empty = np.count_nonzero(neighborhood == 0)
                if neighborhood.size != n_empty + 1:
                    n_similar = np.count_nonzero(neighborhood == value) - 1
                    mean_ratio += n_similar / (neighborhood.size - n_empty - 1)
                    count += 1
        return mean_ratio / count

    def simulation(self):
        for (row, col), value in np.ndenumerate(self.city):
            if value != 0:
                neighborhood = np.roll(self.city, (1-row, 1-col),
                                       axis=(0, 1))[:3, :3]
                n_empty = np.count_nonzero(neighborhood == 0)
                if neighborhood.size != n_empty + 1:
                    n_similar = np.count_nonzero(neighborhood == value) - 1
                    ratio = n_similar / (neighborhood.size - n_empty - 1)
                    if ratio < self.intolerance:
                        empty_houses = np.argwhere(self.city == 0)
                        random_x, random_y = self.rng.choice(empty_houses)
                        self.city[random_x, random_y] = value
                        self.city[row, col] = 0

    def _control(self, x, y):
        value = self.city[x, y]
        neighborhood = np.roll(self.city, (1-x, 1-y),
                               axis=(0, 1))[:3, :3]
        n_empty = np.count_nonzero(neighborhood == 0)
        if neighborhood.size != n_empty + 1:
            n_similar = np.count_nonzero(neighborhood == value) - 1
            ratio = n_similar / (neighborhood.size - n_empty - 1)
            if ratio < self.intolerance:
                empty_houses = np.argwhere(self.city == 0)
                random_x, random_y = self.rng.choice(empty_houses)
                self.city[random_x, random_y] = value
                self.city[x, y] = 0


st.write("""
# Interactive Schelling Model
*by Alessandro Romancino*
""")

city_length = st.sidebar.slider('City Length', 10, 500, 100, 10)
empty_ratio = st.sidebar.slider('Empty Houses Ratio', 0.0, 1.0, .2)
intolerance = st.sidebar.slider('Intolerance Threshold', 0.0, 1.0, .4)
n_ethnicities = st.sidebar.slider(
    'Number of Different Ethnicities', 2, 6, 2, 1)
n_iterations = st.sidebar.number_input(
    'Number of Steps (Iterations)', 1, 1000, 20)
seed = st.sidebar.number_input('Seed', -10000, 10000, 1234)

schelling = Schelling(city_length, empty_ratio, intolerance, n_ethnicities, seed)
mean_ratio = schelling.similarity_ratio()
print(f'{mean_ratio=}')


plt.figure(figsize=(6, 9))
plt.style.use('ggplot')

colormap = cm.get_cmap('viridis').copy()
colormap.set_under('w')

plt.subplot2grid((3, 1), (0, 0), rowspan=2)
plt.axis('off')
plt.grid(False)
plt.pcolormesh(schelling.city, cmap=colormap, vmin=1,
               vmax=n_ethnicities)

plt.subplot2grid((3, 1), (2, 0))
plt.xlabel('Iterations')
plt.xlim([0, n_iterations])
plt.ylim([0, 1])
plt.title(f'Similarity Ratio Average {mean_ratio:.3f}')

progress_bar = st.progress(0)
city_plot = st.pyplot(plt)

mean_ratio_array = [mean_ratio]
if st.sidebar.button('Run Simulation'):
    for i in range(n_iterations):
        schelling.simulation()
        mean_ratio = schelling.similarity_ratio()
        mean_ratio_array.append(mean_ratio)

        plt.figure(figsize=(6, 9))

        plt.subplot2grid((3, 1), (0, 0), rowspan=2)
        plt.axis('off')
        plt.grid(False)
        plt.pcolormesh(schelling.city, cmap=colormap, vmin=1,
                    vmax=n_ethnicities)
        
        plt.subplot2grid((3, 1), (2, 0))
        plt.xlabel('Iterations')
        plt.xlim([0, n_iterations])
        plt.ylim([0, 1])
        plt.title(f'Similarity Ratio Average {mean_ratio:.3f}', fontsize=15)
        plt.plot(mean_ratio_array)

        city_plot.pyplot(plt)
        plt.close('all')
        progress_bar.progress((i+1)/n_iterations)