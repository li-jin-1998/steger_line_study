import numpy as np
import matplotlib.pyplot as plt
import imageio
import os

from PIL import Image


def fit_line(points):
    """Fit a line to the given points and return the slope and intercept."""
    x = points[:, 0]
    y = points[:, 1]
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    return m, c


def compute_intersection(m1, c1, m2, c2):
    """Compute the intersection point of two lines."""
    x_intersect = (c2 - c1) / (m1 - m2)
    y_intersect = m1 * x_intersect + c1
    return x_intersect, y_intersect


def compute_angle(m1, m2):
    """Compute the angle between two lines given their slopes."""
    v1 = np.array([1, m1])
    v2 = np.array([1, m2])
    cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    theta = np.arccos(cos_theta)
    theta_degrees = np.degrees(theta)
    supplementary_angle = 180 - theta_degrees
    return theta_degrees, supplementary_angle


def plot_lines_and_points(points, m1, c1, m2, c2, intersection, theta_degrees, supplementary_angle, split_index, frame):
    """Plot the points, fitted lines, and intersection point."""
    plt.figure(figsize=(10, 6))

    # Plot all points in blue
    plt.scatter(points[:, 0], points[:, 1], color='blue', label='Points')

    # Highlight the points used for the best fit in red and green
    plt.scatter(points[split_index - 4:split_index + 1, 0], points[split_index - 4:split_index + 1, 1], color='red',
                label='Fit Points 1')
    plt.scatter(points[split_index:split_index + 5, 0], points[split_index:split_index + 5, 1], color='green',
                label='Fit Points 2')

    # Plot the fitted lines
    x_fit = np.linspace(min(points[:, 0]) - 1, max(points[:, 0]) + 1, 100)
    y_fit1 = m1 * x_fit + c1
    y_fit2 = m2 * x_fit + c2

    plt.plot(x_fit, y_fit1, 'r--', label=f'Fit Line 1: y = {m1:.2f}x + {c1:.2f}')
    plt.plot(x_fit, y_fit2, 'g--', label=f'Fit Line 2: y = {m2:.2f}x + {c2:.2f}')

    # Plot the intersection point
    plt.scatter(*intersection, color='purple', label='Intersection')

    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(
        f'Two Lines and Their Angle: {theta_degrees:.2f} Degrees\nSupplementary Angle: {supplementary_angle:.2f} Degrees')
    plt.legend()
    plt.grid(True)

    # Save the plot as an image
    filename = f'frame_{frame:02d}.png'
    plt.savefig(filename)
    plt.close()
    return filename


# Generate random points around two linear trends
np.random.seed(42)
x1 = np.linspace(1, 10, 10)
y1 = 2 * x1 + np.random.normal(0, 1, len(x1))

x2 = np.linspace(11, 20, 10)
y2 = 5 * x2 - 30 + np.random.normal(0, 1, len(x2))

points = np.vstack((np.column_stack((x1, y1)), np.column_stack((x2, y2))))

max_angle = 0
best_split = None
best_fit = None
filenames = []

# Traverse all possible split points, using only 5 points before and 5 points after each split
for pt in range(4, len(points) - 4):
    m1, c1 = fit_line(points[pt - 4:pt + 1])
    m2, c2 = fit_line(points[pt:pt + 5])

    theta_degrees, supplementary_angle = compute_angle(m1, m2)

    if theta_degrees > max_angle:
        max_angle = theta_degrees
        best_split = pt
        best_fit = (m1, c1, m2, c2)

    intersection = compute_intersection(m1, c1, m2, c2)
    filename = plot_lines_and_points(points, m1, c1, m2, c2, intersection, theta_degrees, supplementary_angle, pt,
                                     len(filenames))
    filenames.append(filename)

# 打开图像文件并转换为Pillow图像对象
images = [Image.open(image) for image in filenames]

# 保存为GIF文件
images[0].save(
    'fit_lines.gif',
    save_all=True,
    append_images=images[1:],
    duration=500,  # 每帧的显示时间（毫秒）
    loop=0  # 循环次数（0 表示无限循环）
)

# # Create a gif
# with imageio.get_writer('fit_lines.gif', mode='I', duration=100,loop=0) as writer:
#     for filename in filenames:
#         image = imageio.imread_v2(filename)
#         writer.append_data(image)

# Remove the images
for filename in filenames:
    os.remove(filename)

print(f'Best split point: {best_split}, Max angle: {max_angle:.2f} degrees')
