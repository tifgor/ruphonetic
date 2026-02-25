import matplotlib.pylab as plt

def show_plot(dct):
    lists = dct.items()
    x, y = zip(*lists)
    plt.plot(x, y)
    plt.show()

def show_pie_plot(dct):
    labels = []
    sizes = []

    for x, y in dct.items():
        labels.append(x)
        sizes.append(y)

    plt.pie(sizes, labels=labels)

    plt.axis('equal')
    plt.show()

def show_bar_plot(dct):
    plt.bar(range(len(dct)), list(dct.values()), align='center')
    plt.xticks(range(len(dct)), list(dct.keys()))
    plt.show()

def show_plots(dct, plot, pie_plot, bar_plot):
    if plot:
        show_plot(dct)
    if pie_plot:
        show_pie_plot(dct)
    if bar_plot:
        show_bar_plot(dct)