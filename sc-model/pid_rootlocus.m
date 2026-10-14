%% PID tuning for one attitude axis in Control System Designer
% Plant: one axis, I * theta'' = T. Scaled so the app's plots read in physical units:
%   input  du = 1  ->  the eclipse torque step dT on the weakest (smallest inertia) axis
%   output y       ->  attitude error [arcsec]
% so in the app:
%   Impulse du -> y  =  rate error after the eclipse step [arcsec/s]   (limit 0.3)
%   Step    du -> y  =  attitude error after the eclipse step [arcsec] (limit 360 = 0.1 deg)
% Because every axis' gains are scaled by its own inertia, all three axes get the same poles,
% so tuning this one loop tunes all three.
%
% Use:
%   1. Run. The app opens on the root locus with the current sim design loaded.
%   2. In the app: New Plot > Impulse > du to y   (and New Plot > Step > du to y if you like).
%   3. Drag the poles/zeros on the root locus until the impulse peak is below 0.3.
%   4. Export > select C > Export (puts C in the workspace), then press Enter in the command window.
%   5. The script prints the gains for attitude_sim.py and plots the check.

clear; close all;

%% Inputs
I = [921.825, 1035.753, 493.689];   % [kg m^2] diag of the inertia, ops phase (spacecraft.mass_properties)
dT = 3e-4;                          % [N m] torque step at eclipse entry/exit (from the sim)
RATE_LIMIT = 0.3;                   % [arcsec/s] stability requirement
POINT_LIMIT = 360;                  % [arcsec] accuracy requirement, 0.1 deg
w_start = 0.15;                     % [rad/s] starting design: triple pole at -w_start (the current sim)
OPEN_DESIGNER = true;               % false: skip the app and check C_start

arcsec = 180 / pi * 3600;           % [arcsec/rad]
a = dT / min(I) * arcsec;           % plant scale: eclipse step -> arcsec/s^2
s = tf('s');
G = a / s^2;                        % du (eclipse steps) -> y (arcsec)

% Starting PID, (s + w)^3 closed loop: C = (3w s^2 + 3w^2 s + w^3) / s, divided by the plant scale
w = w_start;
C_start = zpk((3*w*s^2 + 3*w^2*s + w^3) / s / a);

%% Tune
if OPEN_DESIGNER
    controlSystemDesigner('rlocus', G, C_start);
    input(sprintf(['\nTune in the app, then Export > C to the workspace and press Enter here.\n' ...
                   'Impulse du->y peak must stay below %.1f (arcsec/s).\n'], RATE_LIMIT), 's');
end
if exist('C', 'var')
    C = tf(C);
else
    fprintf('No exported C found, checking the starting design.\n');
    C = tf(C_start);
end

%% Gains: C = (Kd s^2 + Kp s + Ki) / s in app units -> physical [Nm/rad] per axis
[num, den] = tfdata(C, 'v');
num = num(find(num, 1):end);  den = den(find(den, 1):end);   % strip leading zeros
if numel(den) == 2 && den(2) == 0 && numel(num) <= 3          % PID / PI / I: one pole at 0
    coef = [zeros(1, 3 - numel(num)), num] / den(1);           % [Kd Kp Ki]
elseif numel(den) == 1 && numel(num) <= 2                     % PD / P: no integrator
    coef = [zeros(1, 2 - numel(num)), num, 0] / den(1);
else
    error('C is not a PID: keep at most two zeros and one pole at the origin.');
end
Kd = coef(1) * a * I;  Kp = coef(2) * a * I;  Ki = coef(3) * a * I;

CL_poles = pole(feedback(G * C, 1));
fprintf('\nClosed-loop poles [rad/s]:\n'); disp(CL_poles);
if any(real(CL_poles) < -0.5)
    warning('Poles left of -0.5 rad/s: the 1 s Euler step in attitude_sim.py gets inaccurate.');
end
fprintf('Paste into attitude_sim.py (replaces Kp/Kd/Ki):\n');
fprintf('Kp = np.array([%.6g, %.6g, %.6g])   # [Nm/rad]\n', Kp);
fprintf('Kd = np.array([%.6g, %.6g, %.6g])   # [Nm s/rad]\n', Kd);
fprintf('Ki = np.array([%.6g, %.6g, %.6g])   # [Nm/(rad s)]\n\n', Ki);

%% Check: eclipse torque step on the weakest axis
dist = feedback(G, C);                          % du -> y [arcsec]
t = linspace(0, 200, 4000);
theta = step(dist, t);                          % attitude error [arcsec]
rate = impulse(dist, t);                        % rate error [arcsec/s]

figure('Name', 'Eclipse step response');
subplot(2, 1, 1);
plot(t, theta, 'LineWidth', 1.2); grid on;
ylabel('Attitude error [arcsec]');
title(sprintf('%.0f \\muN m step, I = %.0f kg m^2: max %.2f" (limit %.0f")', ...
      dT * 1e6, min(I), max(abs(theta)), POINT_LIMIT));
subplot(2, 1, 2);
plot(t, rate, 'LineWidth', 1.2); grid on; hold on;
yline(RATE_LIMIT, '--r', sprintf('requirement %.1f"/s', RATE_LIMIT));
ylabel('Rate error [arcsec/s]'); xlabel('Time [s]');
title(sprintf('max %.3f"/s', max(abs(rate))));

figure('Name', 'Bode with margins');
margin(G * C);
