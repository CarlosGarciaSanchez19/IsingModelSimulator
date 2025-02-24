
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class IsingModelClass:

	kB = 1.38064852e-23

	def __str__(self):
		return (f"2D Ising Model with {self.size}x{self.size} spins\n"
	+ f"T = {self.temperature:.2f} K\nJ = {self.J} Jules\nh = {self.h} Jules\n"
	+ f"Curie temperature: {self.calc_curie_temperature():.2f} K")

	def __init__(self, size, temperature, J=1, h=0): 
		self.size = size
		self.temperature = temperature
		self.J = J
		self.h = h
		self.spins = np.random.choice([-1, 1], size=(size, size))
	
	def reset_model(self): # Reset the model to its initial state
		self.spins = np.random.choice([-1, 1], size=(self.size, self.size))
		if hasattr(self, "magnetizations"):
			delattr(self, "magnetizations")

	def calc_curie_temperature(self):
		return 2 * self.J / (self.kB * np.log(1 + np.sqrt(2)))

	def calc_energy_change(self, i, j): # Energy change of flipping a spin
		neighbors = (
			self.spins[(i + 1) % self.size, j] +
			self.spins[(i - 1) % self.size, j] +
			self.spins[i, (j + 1) % self.size] +
			self.spins[i, (j - 1) % self.size]
		)
		return 2 * self.J * self.spins[i, j] * neighbors + 2 * self.h * self.spins[i, j]
	
	def metropolis_step(self): # Perform a single Metropolis step
		i, j = np.random.randint(0, self.size, size=2)
		delta_E = self.calc_energy_change(i, j)

		if delta_E <= 0 or np.random.rand() < np.exp(-delta_E / (self.temperature * self.kB)): # Metropolis criterion (Boltzmann distribution)
			self.spins[i, j] *= -1
	
	def simulate(self, steps): # Simulate the model for a given number of steps
		if not hasattr(self, "magnetizations"):
			self.energies = np.zeros(steps)
			self.magnetizations = np.zeros(steps)

			for step in range(steps):
				self.metropolis_step()
				energie = -self.J * np.sum(
					np.multiply(self.spins, np.roll(self.spins, 1, axis=0)) +
					np.multiply(self.spins, np.roll(self.spins, 1, axis=1))
				) - self.h * np.sum(self.spins)
				self.energies[step] = energie
				mag = np.sum(self.spins) / self.size**2
				self.magnetizations[step] = mag
				if step % (steps // 10) == 0:
					print(f"Step {step}/{steps} completed.")

		return self.energies, self.magnetizations
	
	def animate(self, steps, file_name="ising_model", cmap="spring"): # Create an animation of the model
		self.fst_frame = True
		if steps < 150:
			self.frames = steps
		self.frames = 150
		fig, ax = plt.subplots(figsize=(6, 6))
		ax.set_title(f"Ising Model at T = " 
			   + str(self.temperature) + " K,\n Interaction strenght of " 
			   + str(self.J) + " J\n and an external magnetic field of " 
			   + str(self.h) + " J")
		ax.set_xlim(0, self.size)
		ax.set_ylim(0, self.size)
		im = ax.imshow(self.spins, cmap=cmap, vmin=-1, vmax=1)
		fig.colorbar(im, ax=ax, label='Spin')

		if hasattr(self, "magnetizations"):
			delattr(self, "magnetizations")

		if hasattr(self, "energies"):
			delattr(self, "energies")

		self.energies = np.zeros(self.frames)
		self.magnetizations = np.zeros(self.frames)

		def update(frame): # Update the animation and calculate the energy and magnetization
			if self.fst_frame:
				self.fst_frame = False
			else:
				for _ in range(steps // self.frames):
					self.metropolis_step()
			self.energies[frame] = -self.J * np.sum(
				np.multiply(self.spins, np.roll(self.spins, 1, axis=0)) +
				np.multiply(self.spins, np.roll(self.spins, 1, axis=1))
			) - self.h * np.sum(self.spins)
			self.magnetizations[frame] = np.sum(self.spins) / self.size**2
			im.set_array(self.spins)
			return [im]
		
		anim = FuncAnimation(fig, update, frames=self.frames, interval=100, blit=True)
		anim.save(file_name + ".gif", fps=30)
		plt.close()

	def plot_energy(self, steps, cmap="spring"): # Plot the energy of the system vs Monte Carlo steps and the final spin configuration
		energies = self.simulate(steps)[0]
		fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3))

		if hasattr(self, "frames"):
			ax1.plot([i * steps // self.frames for i in range(0, self.frames)], energies, color="red")
		else:
			ax1.plot(energies, color="red")
		ax1.set_title("System energy")
		ax1.set_xlabel("Step")
		ax1.set_ylabel("Energy [J]")

		cax = ax2.imshow(self.spins, cmap=cmap, vmin=-1, vmax=1)
		ax2.set_title("Final spin configuration")
		fig.colorbar(cax, ax=ax2, label='Spin')
	
		plt.tight_layout()
		plt.show()
	
	def plot_magnetization(self, steps, cmap="spring"): # Plot the magnetization of the system vs Monte Carlo steps and the final spin configuration
		magnetizations = self.simulate(steps)[1]
		fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3))

		if hasattr(self, "frames"):
			ax1.plot([i * steps // self.frames for i in range(0, self.frames)], magnetizations, color="blue")
		else:
			ax1.plot(magnetizations, color="blue")
		ax1.set_title("Magnetization")
		ax1.set_xlabel("Step")
		ax1.set_ylabel("Magnetization per spin [J]")

		cax = ax2.imshow(self.spins, cmap=cmap, vmin=-1, vmax=1)
		ax2.set_title("Final spin configuration")
		fig.colorbar(cax, ax=ax2, label='Spin')

		plt.tight_layout()
		plt.show()