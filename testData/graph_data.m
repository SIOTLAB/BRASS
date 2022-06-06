% 5 Flows, 10 Seconds, with reservation

file = dlmread('5F_10S_Rsv.csv',',');
header = file(1,:);
data = file(2:end,:);

f1 = figure(1); hold on
title("5 Flows with 1 Reservation", "fontsize", 40);
xlabel("Time (s)");
ylabel("Transfer Rate (Gbps)");
axis([1 10 0 20]); grid on;
for i = 1:5
  a(i) = plot([1:10], data(:,i), "linewidth", 0.5);
end
legend(a, num2str(transpose(header)), "location", "northeastoutside");
hold off

% 5 Flows, 10 Seconds, without reservation

file = dlmread('5F_10S_noRsv.csv',',');
header = file(1,:);
data = file(2:end,:);

f2 = figure(2); hold on
title("5 Flows without Reservation", "fontsize", 30);
xlabel("Time (s)");
ylabel("Transfer Rate (Gbps)");
axis([1 10 0 20]); grid on;
for i = 1:5
  a(i) = plot([1:10], data(:,i), "linewidth", 0.5);
end
legend(a, num2str(transpose(header)), "location", "northeastoutside");
hold off

f3 = figure(3); hold on
title({"5 Flows without Reservation";"Zoomed in"}, "fontsize", 30);
xlabel("Time (s)");
ylabel("Transfer Rate (Gbps)");
axis([1 10 7.2 7.8]); grid on;
for i = 1:5
  a(i) = plot([1:10], data(:,i), "linewidth", 0.5);
end
legend(a, num2str(transpose(header)), "location", "northeastoutside");
hold off

% 20 Flows, 200 Seconds, with reservation

file = dlmread('20F_300S_Rsv.csv',',');
header = file(1,:);
data = file(2:end,:);

f4 = figure(4); hold on
title("20 Flows with 1 Reservation", "fontsize", 30);
xlabel("Time (s)");
ylabel("Transfer Rate (Gbps)");
axis([1 300 0 20]); grid on;
for i = 1:20
  a(i) = plot([1:300], data(:,i), "linewidth", 0.5);
end
legend(a, num2str(transpose(header)), "location", "northeastoutside");
hold off

% 20 Flows, 200 Seconds, without reservation

file = dlmread('20F_300S_noRsv.csv',',');
header = file(1,:);
data = file(2:end,:);

f5 = figure(5); hold on
title("20 Flows without Reservation", "fontsize", 30);
xlabel("Time (s)");
ylabel("Transfer Rate (Gbps)");
axis([1 300 0 20]); grid on;
for i = 1:20
  a(i) = plot([1:300], data(:,i), "linewidth", 0.5);
end
legend(a, num2str(transpose(header)), "location", "northeastoutside");
hold off

% Export graphs
print(f1, "plot_5F_10S_Rsv.svg", "-landscape", "-Fsilka:10");
print(f2, "plot_5F_10S_noRsv.svg", "-landscape", "-Fsilka:10");
print(f3, "plot_5F_10S_noRsv_zoom.svg", "-landscape", "-Fsilka:10");
print(f4, "plot_20F_300S_Rsv.svg", "-landscape", "-Fsilka:10");
print(f5, "plot_20F_300S_noRsv.svg", "-landscape", "-Fsilka:10");