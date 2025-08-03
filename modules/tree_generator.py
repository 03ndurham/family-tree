from datetime import date



# Test Class used only for Building App
class Person:
    def __init__(self, id, name, dob, dod=None):
        self.id = id
        self.name = name
        self.dob = dob
        self.dod = dod
        self.parents = []

# Sample data
jim = Person(1, "James T. Durham", date(1959, 10, 11))
carole = Person(2, "Carole L. Cruikshank", date(1960, 10, 11))
heather = Person(3, "Heather D. Durham", date(1981, 9, 17))
nathan = Person(4, "Nathan J. Durham", date(1985, 5, 28))
isabella = Person(5, "Isabella C. Hernandez", date(2005, 7, 18))

# Set relationships
heather.parents = [jim, carole]
nathan.parents = [jim, carole]
isabella.parents = [heather]

# ---------------------------------------------
# FAMILY TREE PLOTTER (Timeline-Based Layout)
# ---------------------------------------------
# GOAL:
# Visualize a family tree where:
# - X-axis represents time (based on date of birth)
# - Y-axis is a "relationship position" (not time-based)
# - Couples are shown as a shared connection point
# - Children descend from the midpoint between both parents
# - Layout attempts to avoid overlapping lines or nodes
# ---------------------------------------------

# STEP 1: Identify Foundational Generation
# ---------------------------------------------
# - Define "Gen 0" as any person who has no listed parents
# - Evenly distribute Gen 0 along the Y-axis
# - Place them on the X-axis using their date of birth

# STEP 2: Determine Couples
# ---------------------------------------------
# - If a child has two listed parents, treat those two people as a "couple"
# - Couples should have a horizontal line drawn between them
# - This line represents the union from which the child(ren) descend

# STEP 3: Position Children
# ---------------------------------------------
# - X-axis: determined by each child's date of birth
# - Y-axis: place children roughly centered vertically between their parents
#   (e.g., average Y of parents)
# - Introduce a vertical line that descends from the couple’s midline down to the child(ren)

# STEP 4: Layout Considerations
# ---------------------------------------------
# - For now, consider horizontal layout (X = DOB, Y = relationship level)
# - Later, this can be rotated for vertical trees if needed
# - Use a spacing algorithm to avoid overlapping nodes or lines
# - Ideal spacing might include nudging members and applying basic repulsion rules

# STEP 5: Node Positioning Rules
# ---------------------------------------------
# - No node (person box) should overlap a connecting line
# - The system should attempt to move nodes (within reason) to reduce clutter
# - Aim for symmetric appearance where possible
# - In dense trees, children of the same couple should be aligned horizontally (or vertically if layout is rotated)

# STEP 6: Drawing Rules
# ---------------------------------------------
# - Draw person nodes with name + DOB
# - Draw a horizontal line between partners (the “couple line”)
# - Draw vertical lines down to their child(ren) from that line
# - Draw lines from each parent up to the couple line

# FUTURE EXPANSION IDEAS:
# ---------------------------------------------
# - Introduce support for remarriage and step-families
# - Allow hovering over a person to show extended info
# - Export to interactive HTML using Plotly or D3.js
# - Add layout smoothing using force-directed layout or simulated annealing

# IMPLEMENTATION PLAN:
# ---------------------------------------------
# 1. Load members and relationships from your database
# 2. Create graph structure with parent/child and couple relationships
# 3. Assign X and Y positions based on DOB and generation logic
# 4. Draw using matplotlib for static prototype (or Plotly later)
# 5. Iterate on spacing rules and visual polish


def count_gen_zero(family):
    count = 0
    
    for member in family:
        if not member.parents:
            count += 1
    
    return count
