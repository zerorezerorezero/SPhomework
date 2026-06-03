import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from robot.config import LEG_ORDER, COXIA_L, FEMUR_L, TIBIA_L


class Viewer3D:
    def __init__(self):
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X (forward)')
        self.ax.set_ylabel('Y (left)')
        self.ax.set_zlabel('Z (up)')
        self.ax.view_init(elev=25, azim=-45)
        self.lines = {}
        self.body_poly = None
        self.foot_scatter = None

    def _get_leg_segments(self, leg, controller):
        c = math.radians(leg.coxia)
        f = math.radians(leg.femur)
        t = math.radians(leg.tibia)

        bx, by, bz = leg.base_pos
        s = leg.side_sign

        if s > 0:
            cdir = (math.sin(c), math.cos(c))
        else:
            cdir = (math.sin(c), -math.cos(c))

        hx = bx + cdir[0] * COXIA_L
        hy = by + cdir[1] * COXIA_L
        hz = bz

        cos_f = math.cos(f)
        kx = hx + cdir[0] * FEMUR_L * cos_f
        ky = hy + cdir[1] * FEMUR_L * cos_f
        kz = hz + FEMUR_L * math.sin(f)

        total = f + t
        fx = kx + cdir[0] * TIBIA_L * math.cos(total)
        fy = ky + cdir[1] * TIBIA_L * math.cos(total)
        fz = kz + TIBIA_L * math.sin(total)

        return (bx, by, bz), (hx, hy, hz), (kx, ky, kz), (fx, fy, fz)

    def render(self, controller):
        self.ax.clear()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.view_init(elev=25, azim=-45)

        body_x, body_y, body_z = controller.body_x, controller.body_y, controller.body_z
        bl = 50
        bw = 35
        bh = 14

        body_corners = [
            (body_x + bl, body_y + bw, body_z - bh),
            (body_x + bl, body_y - bw, body_z - bh),
            (body_x - bl, body_y - bw, body_z - bh),
            (body_x - bl, body_y + bw, body_z - bh),
            (body_x + bl, body_y + bw, body_z + bh),
            (body_x + bl, body_y - bw, body_z + bh),
            (body_x - bl, body_y - bw, body_z + bh),
            (body_x - bl, body_y + bw, body_z + bh),
        ]

        faces = [
            [body_corners[0], body_corners[1], body_corners[2], body_corners[3]],
            [body_corners[4], body_corners[5], body_corners[6], body_corners[7]],
            [body_corners[0], body_corners[1], body_corners[5], body_corners[4]],
            [body_corners[2], body_corners[3], body_corners[7], body_corners[6]],
            [body_corners[0], body_corners[3], body_corners[7], body_corners[4]],
            [body_corners[1], body_corners[2], body_corners[6], body_corners[5]],
        ]

        body_poly = Poly3DCollection(faces, alpha=0.3, facecolor='#4477aa', edgecolor='#2255aa', linewidth=1)
        self.ax.add_collection3d(body_poly)

        leg_colors = ['#cc3333', '#cc6633', '#33aa33', '#3366cc']
        foot_positions = []
        foot_colors = []

        for i, name in enumerate(LEG_ORDER):
            leg = controller.legs.get(name)
            if leg is None:
                continue
            base, hip, knee, foot = self._get_leg_segments(leg, controller)

            pts_x = [base[0], hip[0], knee[0], foot[0]]
            pts_y = [base[1], hip[1], knee[1], foot[1]]
            pts_z = [base[2], hip[2], knee[2], foot[2]]

            color = leg_colors[i % len(leg_colors)]
            self.ax.plot(pts_x, pts_y, pts_z, color=color, linewidth=3, marker='o',
                         markersize=4, label=name)

            foot_positions.append(foot)
            foot_colors.append(color)

        if foot_positions:
            fx, fy, fz = zip(*foot_positions)
            self.ax.scatter(fx, fy, fz, color=foot_colors, s=40, marker='s')

        self.ax.set_xlim(body_x - 120, body_x + 120)
        self.ax.set_ylim(body_y - 120, body_y + 120)
        self.ax.set_zlim(-60, 60)

        self.ax.legend(loc='upper right', fontsize=8)
        self.ax.set_title('Quadruped Robot Control System')

    def show(self, block=True):
        plt.tight_layout()
        plt.show(block=block)

    def pause(self, interval=0.01):
        plt.pause(interval)
