import math
import random

class MCTSNode:
    def __init__(self, state, parent=None, action=None, all_place_names=None):
        self.state = state  # List of attraction names
        self.parent = parent
        self.action = action  # The attraction added to get to this state
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_actions = [name for name in all_place_names if name not in state] if all_place_names else []

    def select_child(self):
        # UCB1 Selection formula
        if not self.children:
            return None
        return max(self.children, key=lambda c: (c.wins / c.visits) + 2.0 * math.sqrt(math.log(self.visits) / c.visits))

    def add_child(self, action, state, all_place_names):
        child = MCTSNode(state, parent=self, action=action, all_place_names=all_place_names)
        if action in self.untried_actions:
            self.untried_actions.remove(action)
        self.children.append(child)
        return child

    def update(self, reward):
        self.visits += 1
        self.wins += reward

def select_best_attractions(all_attractions, budget, duration=1, iterations=500):
    """
    Uses MCTS to select a subset of attractions that fits the budget and maximizes rating.
    """
    if not all_attractions:
        return []

    max_places = 4 * duration # Target about 4 places per day
    place_names = [a['place_name'] for a in all_attractions]
    attr_map = {a['place_name']: a for a in all_attractions}
    
    root = MCTSNode(state=[], all_place_names=list(place_names))

    for _ in range(iterations):
        node = root
        
        # 1. Selection: Move down the tree while all children are expanded
        while not node.untried_actions and node.children:
            node = node.select_child()
            
        # 2. Expansion: Add a new child if budget and max_places allow
        if node.untried_actions and len(node.state) < max_places:
            action = random.choice(node.untried_actions)
            node.untried_actions.remove(action)
            # Simple budget check before expansion to avoid wasting iterations
            if sum(attr_map[s]['avg_fee'] for s in node.state) + attr_map[action]['avg_fee'] <= budget:
                new_state = node.state + [action]
                node = node.add_child(action, new_state, place_names)
            
        # 3. Simulation (Rollout)
        state = list(node.state)
        possible = [name for name in place_names if name not in state]
        random.shuffle(possible)
        
        for name in possible:
            if len(state) >= max_places: break
            if sum(attr_map[s]['avg_fee'] for s in state) + attr_map[name]['avg_fee'] <= budget:
                state.append(name)
            
        # Evaluation (Reward function)
        total_rating = sum(attr_map[name]['avg_rating'] for name in state)
        if state:
            # Reward both quality and quantity
            reward = (total_rating / len(state)) * len(state)
        else:
            reward = 0
            
        # 4. Backpropagation
        curr = node
        while curr:
            curr.update(reward)
            curr = curr.parent
            
    # Trace the most visited path from root
    best_path = []
    curr = root
    while curr.children:
        curr = max(curr.children, key=lambda c: c.visits)
        best_path.append(curr.action)
    
    return [attr_map[name] for name in best_path]

if __name__ == '__main__':
    # Test stub
    mock_data = [
        {'place_name': 'A', 'avg_rating': 5, 'avg_fee': 1000},
        {'place_name': 'B', 'avg_rating': 4, 'avg_fee': 200},
        {'place_name': 'C', 'avg_rating': 3, 'avg_fee': 100},
        {'place_name': 'D', 'avg_rating': 4.5, 'avg_fee': 500},
    ]
    selected = select_best_attractions(mock_data, budget=800)
    print("MCTS Selected:")
    for s in selected:
        print(f"- {s['place_name']} (Rating: {s['avg_rating']}, Fee: {s['avg_fee']})")
