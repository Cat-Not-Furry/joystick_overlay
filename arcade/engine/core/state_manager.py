# core/state_manager.py
# Maquina de estados para navegacion en una sola ventana Pygame.


class BaseState:
	"""Estado base: sobreescribe handle_events, update, draw."""

	def enter(self, ctx):
		pass

	def exit(self, ctx):
		pass

	def handle_events(self, ctx, events):
		"""Retorna siguiente estado (BaseState) o None para mantener el actual."""
		return None

	def update(self, ctx, dt):
		pass

	def draw(self, ctx, screen):
		pass


class StateManager:
	"""Gestor de estado actual con transiciones explicitas."""

	def __init__(self, initial_state, ctx):
		self.ctx = ctx
		self.state = initial_state
		if self.state is not None:
			self.state.enter(ctx)

	def set_state(self, new_state):
		if self.state is not None:
			self.state.exit(self.ctx)
		self.state = new_state
		if self.state is not None:
			self.state.enter(self.ctx)

	def handle_events(self, events):
		if self.state is None:
			return
		next_state = self.state.handle_events(self.ctx, events)
		if next_state is not None:
			self.set_state(next_state)

	def update(self, dt):
		if self.state is not None:
			self.state.update(self.ctx, dt)

	def draw(self, screen):
		if self.state is not None:
			self.state.draw(self.ctx, screen)
