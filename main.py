from math import sqrt, sin, cos, radians, ceil, pi
import sys
from random import randrange, uniform
from PyQt6.QtCore import Qt, QRect, QPoint, QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QSlider, QSpinBox, QComboBox, QLabel, QRadioButton, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QLineEdit, QColorDialog
from PyQt6.QtGui import QPainter, QPen, QColor, QPolygon, QBrush, QFont, QPalette

class Planet():
	def __init__(self, center):
		self.center = center
		self.radius = 1 #км
		self.soi_radius = 1 #км
		self.lpo = 1 #км
		self.parent = None
		self.orbit_height = 0 #км
		self.alpha = uniform(0, 2*pi)
		self.color = QColor(randrange(0, 256, 1), randrange(0, 256, 1), randrange(0, 256, 1))
		self.angle_ratio = 0.01
		self.name = ""

	def setRadius(self, radius):
		self.radius = radius

	def setSOIRadius(self, soi_radius):
		self.soi_radius = soi_radius

	def setLPO(self, lpo):
		self.lpo = lpo

	def setParent(self, parent):
		self.parent = parent
		self.angle_ratio = self.parent.angle_ratio * 10

	def setOrbitHeight(self, orbit_height):
		self.orbit_height = orbit_height

	def setName(self, name):
		self.name = name

	def setColor(self, color):
		self.color = color

	def autoCenter(self):
		if self.parent is not None:
			self.center = QPoint(self.parent.center.x() + self.parent.radius + self.orbit_height, self.parent.center.y())
		else:
			raise ValueError("Could not center object without selected parent.")
	
	def move(self, angle):
		if self.parent is not None:
			self.alpha += angle * self.angle_ratio
			self.center = QPoint(round(self.parent.center.x() + (self.parent.radius + self.orbit_height) * cos(self.alpha)), round(self.parent.center.y() + (self.parent.radius + self.orbit_height) * sin(self.alpha)))
		else:
			raise ValueError("Could not move object without selected parent.")

	def draw(self, painter, scale):
		paint_rad = round(self.radius * scale)
		circle_area = QRect(self.center.x() - paint_rad, self.center.y() - paint_rad, paint_rad * 2, paint_rad * 2)
		pen = QPen()
		pen.setColor(QColor(self.color.red(), self.color.green(), self.color.blue()))
		pen.setStyle(Qt.PenStyle.SolidLine)
		pen.setWidth(2)
		painter.setPen(pen)
		painter.setBrush(QColor(self.color.red(), self.color.green(), self.color.blue(), 90))
		painter.drawEllipse(circle_area)			

	def draw_zone(self, painter, scale, color):
		soi_rad = round((self.radius + self.soi_radius) * scale)
		lpo_rad = round((self.radius + self.lpo) * scale)
		soi_area = QRect(self.center.x() - soi_rad, self.center.y() - soi_rad, soi_rad * 2, soi_rad * 2)
		lpo_area = QRect(self.center.x() - lpo_rad, self.center.y() - lpo_rad, lpo_rad * 2, lpo_rad * 2)
		pen = QPen()
		pen.setColor(color)
		pen.setStyle(Qt.PenStyle.DashLine)
		pen.setWidth(2)
		painter.setPen(pen)
		painter.setBrush(QColor(color.red(), color.green(), color.blue(), round(color.alpha() / 2)))
		painter.drawEllipse(soi_area)
		painter.setBrush(QColor(255, 255, 255, 100))
		painter.drawEllipse(lpo_area)
		self.draw(painter, scale)

	def getGeneration(self):
		cur = self
		cnt = 1
		while cur.parent != None:
			cur = cur.parent
			cnt += 1
		return cnt

class Satellite():
	def __init__(self, center, alpha):
		self.center = center
		self.radius = 3 #км
		self.parent = None
		self.orbit_height = 0 #км
		self.alpha = alpha
		self.color = QColor(0, 255, 63, 100)
		self.angle_ratio = 0.01

	def setParent(self, parent):
		self.parent = parent
		self.angle_ratio = self.parent.angle_ratio * 10

	def setOrbitHeight(self, orbit_height):
		self.orbit_height = orbit_height

	def setColor(self, color):
		self.color = color

	def autoCenter(self):
		if self.parent is not None:
			self.center = QPoint(self.parent.center.x() + self.parent.radius + self.orbit_height, self.parent.center.y())
		else:
			raise ValueError("Could not center object without selected parent.")
	
	def move(self, angle):
		if self.parent is not None:
			self.alpha += angle * self.angle_ratio
			self.center = QPoint(round(self.parent.center.x() + (self.parent.radius + self.orbit_height) * cos(self.alpha)), round(self.parent.center.y() + (self.parent.radius + self.orbit_height) * sin(self.alpha)))
		else:
			raise ValueError("Could not move object without selected parent.")

	def draw(self, painter, scale):
		paint_rad = self.radius
		circle_area = QRect(self.center.x() - paint_rad, self.center.y() - paint_rad, paint_rad * 2, paint_rad * 2)
		pen = QPen()
		pen.setColor(QColor(self.color.red(), self.color.green(), self.color.blue()))
		pen.setStyle(Qt.PenStyle.SolidLine)
		pen.setWidth(2)
		painter.setPen(pen)
		painter.setBrush(QColor(self.color.red(), self.color.green(), self.color.blue(), 90))
		painter.drawEllipse(circle_area)	

class Constellation():
	def __init__(self, parent, const_sz):
		self.parent = parent
		self.orbit_height = parent.lpo #км
		self.satellites = []
		self.name = ""
		angle = 0
		alpha = 2*pi / const_sz
		for i in range(const_sz):
			tmp = Satellite(None, angle)
			tmp.setParent(self.parent)
			tmp.setOrbitHeight(self.orbit_height)
			tmp.autoCenter()
			angle += alpha
			self.satellites.append(tmp)

	def getSize(self):
		return len(self.satellites)

	def setName(self, name):
		self.name = name

	def setOrbitHeight(self, orbit_height):
		self.orbit_height = orbit_height
		for satellite in self.satellites:
			satellite.setOrbitHeight(self.orbit_height)

	def setConstellationSize(self, size):
		self.satellites = []
		angle = 0
		alpha = 2*pi / size
		for i in range(size):
			tmp = Satellite(None, angle)
			tmp.setParent(self.parent)
			tmp.setOrbitHeight(self.orbit_height)
			tmp.autoCenter()
			angle += alpha
			self.satellites.append(tmp)

	def draw(self, painter, scale):
		for index, satellite in enumerate(self.satellites):
			satellite.draw(painter, scale)
			x1 = self.satellites[index].center.x()
			y1 = self.satellites[index].center.y()
			x2 = self.satellites[index+1].center.x() if index != len(self.satellites) - 1 else self.satellites[0].center.x()
			y2 = self.satellites[index+1].center.y() if index != len(self.satellites) - 1 else self.satellites[0].center.y()
			painter.drawLine(x1, y1, x2, y2)

	def move(self, angle):
		for satellite in self.satellites:
			satellite.move(angle)

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Kerbal Satellite Relay Network")
		self.setFixedSize(1300, 900)

		self.objects = []
		main_object = Planet(QPoint(450, 450))
		main_object.setRadius(100)
		main_object.setName("Центр")
		self.objects.append(main_object)
		self.active_obj = 0
		self.constellations = []
		self.active_constellation = None

		canvas = QLabel()
		canvas.setFixedSize(900, 900)

		new_planet = QPushButton(text="☉")
		new_planet.setFont(QFont('Times', 14))
		new_planet.setFixedSize(30, 30)
		new_planet.clicked.connect(self.new_planet)
		self.planet_set = QComboBox()
		self.planet_set.addItem("Центр")
		self.planet_set.setCurrentIndex(self.active_obj)
		self.planet_set.setFixedSize(295, 30)

		self.planet_name = QLineEdit() #20 символов
		self.planet_name.setFixedSize(330, 30)
		self.planet_name.setFont(QFont('', 14))
		self.planet_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.planet_name.setText("Центр")

		planet_selection = QHBoxLayout()
		planet_selection.addWidget(new_planet)
		planet_selection.addWidget(self.planet_set)

		parent_label = QLabel("Центр: ")
		self.parent_input = QComboBox()
		lt1 = QHBoxLayout()
		lt1.addWidget(parent_label)
		lt1.addWidget(self.parent_input)
		obj_radius_label = QLabel("Радиус тела: ")
		self.obj_radius_input = QSpinBox()
		lt2 = QHBoxLayout()
		lt2.addWidget(obj_radius_label)
		lt2.addWidget(self.obj_radius_input)
		orbit_height_label = QLabel("Высота орбиты: ")
		self.orbit_height_input = QSpinBox()
		lt3 = QHBoxLayout()
		lt3.addWidget(orbit_height_label)
		lt3.addWidget(self.orbit_height_input)
		soi_radius_label = QLabel("Высота СТ: ")
		self.soi_radius_input = QSpinBox()
		lt4 = QHBoxLayout()
		lt4.addWidget(soi_radius_label)
		lt4.addWidget(self.soi_radius_input)
		lpo_label = QLabel("Мин. доп. орбита: ")
		self.lpo_input = QSpinBox()
		lt5 = QHBoxLayout()
		lt5.addWidget(lpo_label)
		lt5.addWidget(self.lpo_input)
		color_label = QLabel("Цвет: ")
		self.color_button = QPushButton("Выбрать")
		lt6 = QHBoxLayout()
		lt6.addWidget(color_label)
		lt6.addWidget(self.color_button)

		self.obj_radius_input.setSuffix(" км")
		self.orbit_height_input.setSuffix(" км")
		self.soi_radius_input.setSuffix(" км")
		self.lpo_input.setSuffix(" км")
		self.obj_radius_input.setMinimum(1)
		self.obj_radius_input.setMaximum(2147483647)
		self.orbit_height_input.setMinimum(1)
		self.orbit_height_input.setMaximum(2147483647)
		self.soi_radius_input.setMinimum(1)
		self.soi_radius_input.setMaximum(2147483647)
		self.lpo_input.setMinimum(1)
		self.lpo_input.setMaximum(2147483647)
		self.obj_radius_input.setValue(100)
		self.soi_radius_input.setValue(1)
		self.lpo_input.setValue(1)
		self.orbit_height_input.setMinimum(0)
		self.orbit_height_input.setValue(0)
		self.orbit_height_input.setDisabled(True)
		self.obj_radius_input.editingFinished.connect(self.change_obj_radius)
		self.orbit_height_input.editingFinished.connect(self.change_orbit_height)
		self.soi_radius_input.editingFinished.connect(self.change_soi_radius)
		self.lpo_input.editingFinished.connect(self.change_lpo)
		self.parent_input.activated.connect(self.change_parent)
		self.planet_set.activated.connect(self.activate_object)
		self.planet_name.editingFinished.connect(self.rename_object)
		self.color_button.clicked.connect(self.repaint_object)

		planet_options = QVBoxLayout()
		planet_options.addLayout(planet_selection)
		planet_options.addWidget(self.planet_name)
		planet_options.addLayout(lt1)
		planet_options.addLayout(lt2)
		planet_options.addLayout(lt3)
		planet_options.addLayout(lt4)
		planet_options.addLayout(lt5)
		planet_options.addLayout(lt6)

		constellation_size_label = QLabel("Кол-во спутников: ")
		constellation_height_label = QLabel("Высота орбиты: ")
		self.constellation_size_input = QSpinBox()
		self.constellation_size_input.setMinimum(3)
		self.constellation_size_input.setMaximum(99)
		self.constellation_size_input.setValue(3)
		self.constellation_size_input.editingFinished.connect(self.change_constellation_size)
		self.constellation_size_input.setEnabled(False)
		self.constellation_height_input = QSpinBox()
		self.constellation_height_input.setSuffix(" км")
		self.constellation_height_input.setMinimum(1)
		self.constellation_height_input.setMaximum(2147483647)
		self.constellation_height_input.editingFinished.connect(self.change_constellation_height)
		self.constellation_height_input.setEnabled(False)

		new_constellation = QPushButton(text="🛰")
		new_constellation.setFont(QFont('Times', 14))
		new_constellation.setFixedSize(30, 30)
		new_constellation.clicked.connect(self.new_constellation)

		self.constellation_set = QComboBox()
		self.constellation_set.setFixedSize(295, 30)
		self.constellation_set.activated.connect(self.activate_constellation)

		self.constellation_name = QLineEdit() #20 символов
		self.constellation_name.setFixedSize(330, 30)
		self.constellation_name.setFont(QFont('', 14))
		self.constellation_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.constellation_name.setEnabled(False)
		self.constellation_name.editingFinished.connect(self.rename_constellation)

		lt7 = QHBoxLayout()
		lt7.addWidget(new_constellation)
		lt7.addWidget(self.constellation_set)

		lt8 = QHBoxLayout()
		lt8.addWidget(constellation_size_label)
		lt8.addWidget(self.constellation_size_input)

		lt9 = QHBoxLayout()
		lt9.addWidget(constellation_height_label)
		lt9.addWidget(self.constellation_height_input)

		satellite_options = QVBoxLayout()
		satellite_options.addLayout(lt7)
		satellite_options.addWidget(self.constellation_name)
		satellite_options.addLayout(lt8)
		satellite_options.addLayout(lt9)

		blank = QLabel()
		blank.setFixedSize(20, 30)

		planet_lt = QHBoxLayout()
		planet_lt.addWidget(blank)
		planet_lt.addLayout(planet_options)
		planet_lt.addWidget(blank)

		self.satellite_lt = QHBoxLayout()
		self.satellite_lt.addWidget(blank)
		self.satellite_lt.addLayout(satellite_options)
		self.satellite_lt.addWidget(blank)

		options_lt = QHBoxLayout()

		controls_lt = QVBoxLayout()
		controls_lt.addLayout(planet_lt)
		controls_lt.addLayout(self.satellite_lt)
		controls_lt.addLayout(options_lt)

		main_lt = QHBoxLayout()
		main_lt.addWidget(canvas)
		main_lt.addLayout(controls_lt)

		widget = QWidget()
		widget.setLayout(main_lt)
		widget.setFixedSize(1300, 900)
		self.setCentralWidget(widget)

		self.background_brush = widget.palette().base()

		self.timer = QTimer()
		self.timer.timeout.connect(self.move_satellites)
		self.timer.start(10)

	def move_satellites(self):
		for obj in self.objects:
			if obj.parent is not None:
				obj.move(0.01)

		for constellation in self.constellations:
			constellation.move(0.01)
		self.update()

	def paintEvent(self, event):
		painter = QPainter(self)
		fill = QRect(0, 0, 900, 900)
		painter.setBrush(QBrush(QColor(255, 255, 255))) # White fill
		painter.drawRect(fill)

		for index, obj in enumerate(self.objects):
			obj.draw(painter, 1)
			if index == self.active_obj and obj.parent is not None:
				obj.parent.draw_zone(painter, 1, QColor(0, 0, 0, 20))
				obj.draw_zone(painter, 1, QColor(74, 219, 176, 90))
			elif index == self.active_obj:
				obj.draw_zone(painter, 1, QColor(74, 219, 176, 90))

		for constellation in self.constellations:
			constellation.draw(painter, 1)

		controls_panel = QRect(900, 0, 400, 900)
		painter.setPen(QPen(self.background_brush.color()))
		painter.setBrush(self.background_brush)
		painter.drawRect(controls_panel)

		painter.end()

	def new_planet(self):
		height = round((self.objects[0].lpo + self.objects[0].soi_radius) / 2)
		planet = Planet(None)
		planet.setRadius(1)
		planet.setSOIRadius(1)
		planet.setLPO(1)
		planet.setOrbitHeight(height)
		planet.setParent(self.objects[0])
		planet.setName(self.next_name())
		planet.autoCenter()
		self.objects.append(planet)
		self.active_obj = len(self.objects) - 1
		self.refresh_interface()

	def new_constellation(self):
		constellation = Constellation(self.objects[self.active_obj], 3)
		height = self.objects[self.active_obj].lpo + 1
		constellation.setOrbitHeight(height)
		constellation.setName(self.next_constellation_name())
		self.constellations.append(constellation)
		self.active_constellation = len(self.constellations) - 1
		self.refresh_interface()

	def next_name(self):
		return f'Тело{len(self.objects) + 1}'

	def next_constellation_name(self):
		return f'Созвездие{len(self.constellations) + 1}'

	def change_obj_radius(self):
		self.objects[self.active_obj].setRadius(self.obj_radius_input.value())
		self.refresh_interface()

	def change_orbit_height(self):
		self.objects[self.active_obj].setOrbitHeight(self.orbit_height_input.value())
		self.refresh_interface()

	def change_soi_radius(self):
		self.objects[self.active_obj].setSOIRadius(self.soi_radius_input.value())
		self.refresh_interface()

	def change_lpo(self):
		self.objects[self.active_obj].setLPO(self.lpo_input.value())
		self.refresh_interface()

	def change_parent(self, index):
		self.objects[self.active_obj].setParent(self.objects[[obj.name for obj in self.objects].index(self.parent_input.currentText())])
		self.refresh_interface()

	def change_constellation_size(self):
		self.constellations[self.active_constellation].setConstellationSize(self.constellation_size_input.value())
		self.refresh_interface()

	def change_constellation_height(self):
		self.constellations[self.active_constellation].setOrbitHeight(self.constellation_height_input.value())
		self.refresh_interface()

	def activate_object(self, index):
		self.active_obj = index
		self.refresh_interface()

	def rename_object(self):
		self.objects[self.active_obj].setName(self.planet_name.text())
		self.refresh_interface()

	def activate_constellation(self, index):
		self.active_constellation = self.active_consts()[index]["base"]
		self.refresh_interface()

	def rename_constellation(self):
		self.constellations[self.active_constellation].setName(self.constellation_name.text())
		self.refresh_interface()

	def repaint_object(self):
		color = QColorDialog.getColor(self.objects[self.active_obj].color, self, "Выберите цвет")
		if color.isValid():
			self.objects[self.active_obj].setColor(color)

	def children_max_gen(self, obj):
		children = [1]
		for obji in self.objects:
			if obji.parent == obj:
				children.append(obji.getGeneration())
		return max(children)

	def active_consts(self):
		active_consts = []
		for index, constellation in enumerate(self.constellations):
			if constellation.parent == self.objects[self.active_obj]:
				active_consts.append({"base": index, "obj": constellation})
		return active_consts

	def refresh_interface(self):
		self.planet_set.clear()
		self.planet_set.addItems([obj.name for obj in self.objects])
		self.planet_set.setCurrentIndex(self.active_obj)
		self.parent_input.clear()
		parent = self.objects[self.active_obj].parent
		if parent is None:
			self.orbit_height_input.setMinimum(0)
			self.orbit_height_input.setValue(0)
			self.orbit_height_input.setDisabled(True)
		else:
			if self.orbit_height_input.value() == 0:
				self.orbit_height_input.setDisabled(False)
				self.orbit_height_input.setMinimum(1)
			parent_ind = self.objects.index(parent)
			self.parent_input.addItem(self.objects[parent_ind].name)
			for index in range(len(self.objects)):
				if index != parent_ind and index != self.active_obj and self.objects[index].getGeneration() != 3 and (self.objects[index].getGeneration() + self.children_max_gen(self.objects[self.active_obj])) <= 4:
					self.parent_input.addItem(self.objects[index].name)
			self.parent_input.setCurrentIndex(0)
			self.orbit_height_input.setMinimum(parent.lpo + self.objects[self.active_obj].soi_radius)
			self.orbit_height_input.setMaximum(parent.soi_radius)
			if self.objects[self.active_obj].orbit_height > parent.soi_radius:
				self.objects[self.active_obj].orbit_height = parent.soi_radius
			elif self.objects[self.active_obj].orbit_height < parent.lpo + self.objects[self.active_obj].soi_radius:
				self.objects[self.active_obj].orbit_height = parent.lpo + self.objects[self.active_obj].soi_radius
				#+ self radius
		self.obj_radius_input.setValue(self.objects[self.active_obj].radius)
		self.soi_radius_input.setValue(self.objects[self.active_obj].soi_radius)
		self.lpo_input.setValue(self.objects[self.active_obj].lpo)
		self.orbit_height_input.setValue(self.objects[self.active_obj].orbit_height)
		self.planet_name.setText(self.objects[self.active_obj].name)

		self.constellation_set.clear()
		active_consts = self.active_consts()
		if len(active_consts) == 0:
			self.constellation_size_input.setEnabled(False)
			self.constellation_height_input.setEnabled(False)
			self.constellation_name.setEnabled(False)
		else:
			self.constellation_size_input.setEnabled(True)
			self.constellation_height_input.setEnabled(True)
			self.constellation_name.setEnabled(True)
			self.constellation_set.addItems([const["obj"].name for const in active_consts])
			active_const = 0
			for index, const in enumerate(active_consts):
				if const["base"] == self.active_constellation:
					active_const = index
			self.constellation_set.setCurrentIndex(active_const)
			self.constellation_size_input.setValue(self.constellations[self.active_constellation].getSize())
			self.constellation_height_input.setValue(self.constellations[self.active_constellation].orbit_height)
			self.constellation_name.setText(self.constellations[self.active_constellation].name)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()

	sys.exit(app.exec())