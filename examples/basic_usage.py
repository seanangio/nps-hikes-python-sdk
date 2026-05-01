"""Basic usage examples for the NPS Hikes SDK.

Run with:
    python examples/basic_usage.py
"""

from nps_hikes import Client, ParkNotFoundError

client = Client()

# -- Get all parks --
print("=== All Parks ===")
parks = client.get_parks()
print(f"Total parks: {parks.park_count}, Visited: {parks.visited_count}")
for park in parks.parks[:3]:
    visited = f"visited {park.visit_month} {park.visit_year}" if park.visit_year else "not yet visited"
    print(f"  {park.park_name} ({park.park_code}) - {visited}")
print()

# -- Get a park summary --
print("=== Yosemite Summary ===")
summary = client.get_park_summary("yose")
print(f"{summary.full_name}")
print(f"  Trails: {summary.total_trails} ({summary.hiked_trails} hiked)")
print(f"  Miles: {summary.total_miles:.1f} ({summary.hiked_miles:.1f} hiked)")
print(f"  Sources: TNM={summary.source_breakdown.tnm}, OSM={summary.source_breakdown.osm}")
print()

# -- Get trails with filtering --
print("=== Yosemite Trails (5+ miles) ===")
trails = client.get_trails(park_code="yose", min_length_mi=5.0)
print(f"Found {trails.pagination.total_count} trails")
for trail in trails.trails[:5]:
    print(f"  {trail.trail_name}: {trail.length_miles:.1f} mi ({trail.source})")
print()

# -- Get hiked points --
print("=== Hiked Points (Yosemite) ===")
points = client.get_hiked_points(park_code="yose")
print(f"Found {points.count} hiked points")
for point in points.hiked_points[:3]:
    print(f"  {point.location_name} -> {point.matched_trail_name or 'unmatched'}")
print()

# -- Get aggregate stats --
print("=== Overall Stats ===")
stats = client.get_stats()
print(f"Total trails: {stats.total_trails}")
print(f"Total miles: {stats.total_miles:.1f}")
print(f"Parks: {stats.parks_count}, States: {stats.states_count}")
if stats.longest_trail:
    print(f"Longest: {stats.longest_trail.trail_name} ({stats.longest_trail.length_miles:.1f} mi)")
print()

# -- Get per-park stats --
print("=== Top 5 Parks by Trail Count ===")
park_stats = client.get_park_stats()
for ps in park_stats.parks[:5]:
    print(f"  {ps.park_name}: {ps.trail_count} trails, {ps.total_miles:.1f} mi")
print()

# -- Error handling --
print("=== Error Handling ===")
try:
    client.get_park_summary("xxxx")
except ParkNotFoundError as e:
    print(f"Caught expected error: {e}")
