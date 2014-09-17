DiffTrike system boot and precharge auxiliar system.

Power is applied to the sub-systems by means of relays, such that power can be
enabled/disabled safely by the system controller or user.

To turn ON the trike there must be a procedure that ensures safetty, avoiding
unintended motor turn ON. And there must be a simple way for a human to quickly
turn power OFF in an emergency.

Power controllers such as motor controllers have big capacitance at the power
rails input. This capacitance needs to be charged in a controlled way to avoid
huge inrush currents which cause switch sparking and capacitor accelerated
ageing. It is the task of the precharger to slowly charge the capacitance until
it approaches the system voltage, and only then enable full power to the power
controller.
