import itertools
import json
import os


def load_instance(filepath):
  with open(filepath, 'r') as f:
    return json.load(f)


def evaluate_schedule(schedule, data):
  """Tính f1, f2, f3 ex-post dựa trên Ex-post evaluation từ thời điểm bắt đầu schedule"""
  H = data['H']
  Delta = data['Delta']
  tasks = {t['id']: t for t in data['tasks']}
  edges = data['edges']
  reports = data['reports']
  CI = data['CI']
  price_act = data['price_act']
  price_use = data['price_use']
  access = data['access']

  # 1. Kiểm tra ràng buộc Precedence
  for u, v in edges:
    if schedule[u] + tasks[u]['p'] > schedule[v]:
      return None  # Không khả thi

  # 2. Tính q_it (trạng thái chạy của task tại mỗi khe t)
  # Khe thời gian tính từ 0 đến H-1 trong code Python cho mượt
  q = {t_id: [0] * H for t_id in tasks}
  for t_id, start in schedule.items():
    p = tasks[t_id]['p']
    for t in range(start, min(start + p, H)):
      q[t_id][t] = 1

  # 3. Tính o_t (kho dữ liệu active) và resource check
  o = [0] * H
  for t in range(H):
    active_load = sum(q[t_id][t] * tasks[t_id]['u'] for t_id in tasks)
    if active_load > 0:
      o[t] = 1  # Giả định dung lượng đủ

  # 4. Tính f1 (Carbon emissions trong kgCO2e)
  # f1 = (PUE * Delta / 1000) * sum_t ( CI_t * (P_idle * o_t + sum_i P_i * q_it) )
  PUE = 1.2
  P_idle = 0.5
  f1_val = 0
  for t in range(H):
    dynamic_energy = sum(tasks[t_id]['P'] * q[t_id][t] for t_id in tasks)
    power_t = P_idle * o[t] + dynamic_energy
    f1_val += CI[t] * power_t
  f1_val = (PUE * Delta / 1000.0) * f1_val

  # 5. Tính f2 (Cloud cost trong USD)
  f2_val = 0
  for t in range(H):
    usage_cost = sum(
        price_use[t] * tasks[t_id]['u'] * q[t_id][t] for t_id in tasks
    )
    f2_val += price_act[t] * o[t] + usage_cost
  f2_val = Delta * f2_val

  # 6. Tính f3 (Weighted Data Age - WDA / Freshness penalty)
  f3_val = 0
  for r in reports:
    r_id = r['id']
    A_r = r['A']
    X_r = r['X']
    d_r = r['d'] - 1   chuyển về index 0
    L_r = r['L']
    theta_r = r['theta']
    w_r = r['w']
    act_access = access.get(r_id, [0] * H)

    # C_r: thời điểm hoàn thành báo cáo (max finish của các task trong A_r)
    C_r = max(schedule[i] + tasks[i]['p'] for i in A_r)
    # E_r: thời điểm trích xuất (min start của các task trong X_r)
    E_r = min(schedule[i] for i in X_r)

    # Kiểm tra deadline và consistency window cơ bản
    if C_r > d_r:
      return None  # Vi phạm deadline

    for t in range(H):
      # Tính tuổi đời dữ liệu age_r(t)
      if t < C_r:
        age = t - L_r
      else:
        age = t - E_r

      excess = max(0, age - theta_r)
      f3_val += w_r * act_access[t] * excess

  f3_val = Delta * f3_val
  return {'f1': f1_val, 'f2': f2_val, 'f3': f3_val}


def solve_brute_force(instance_path):
  data = load_instance(instance_path)
  H = data['H']
  tasks = data['tasks']

  # Xây dựng không gian tìm kiếm các thời điểm bắt đầu khả dĩ cho từng task
  task_ids = [t['id'] for t in tasks]
  ranges = []
  for t in tasks:
    t_id = t['id']
    p = t['p']
    rho = t['rho'] - 1  # index 0
    # Giới hạn khe bắt đầu để task kịp hoàn thành trong H
    max_start = H - p
    ranges.append(range(rho, max_start + 1))

  pareto_front = []
  all_solutions = []

  # Duyệt vét cạn qua mọi tổ hợp
  for combination in itertools.product(*ranges):
    schedule = dict(zip(task_ids, combination))
    objs = evaluate_schedule(schedule, data)
    if objs is not None:
      sol = {'schedule': schedule, 'objectives': objs}
      all_solutions.append(sol)

  # Lọc tập Pareto tối ưu (Non-dominated sorting đơn giản)
  for sol in all_solutions:
    is_dominated = False
    f1, f2, f3 = sol['objectives']['f1'], sol['objectives']['f2'], sol['objectives']['f3']

    for other in all_solutions:
      of1, of2, of3 = other['objectives']['f1'], other['objectives']['f2'], other['objectives']['f3']
      # other trội hơn sol khi tất cả mục tiêu nhỏ hơn hoặc bằng và ít nhất một mục tiêu nhỏ hơn hẳn
      if (of1 <= f1 and of2 <= f2 and of3 <= f3) and (of1 < f1 or of2 < f2 or of3 < f3):
        is_dominated = True
        break

    if not is_dominated:
      pareto_front.append(sol)

  return {'all_feasible': all_solutions, 'pareto_front': pareto_front}


if __name__ == '__main__':
  os.makedirs('expected', exist_ok=True)
  input_dir = 'instances/small'

  if os.path.exists(input_dir):
    for filename in os.listdir(input_dir):
      if filename.endswith('.json'):
        path = os.path.join(input_dir, filename)
        print(f'Đang chạy vét cạn cho: {filename}...')
        result = solve_brute_force(path)

        out_path = os.path.join('expected', filename)
        with open(out_path, 'w') as f:
          json.dump(result, f, indent=2)
        print(f'Đã lưu kết quả chuẩn vào: {out_path}')
  else:
    print(
        f"Thư mục '{input_dir}' chưa tồn tại. Hãy tạo thư mục và đưa các file"
        ' JSON DAG nhỏ vào trước.'
    )
