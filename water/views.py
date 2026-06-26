from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

csv_file = BASE_DIR / "Daily_Water_Intake.csv"

class WaterIntakeView(ViewSet):

    def post(self, request):

        try:
            # Load dataset
            data = pd.read_csv(csv_file)

            # Remove extra spaces from column names
            data.columns = data.columns.str.strip()

            gender = str(request.data.get("gender", "")).strip()
            weight = float(request.data.get("weight", 0))
            age = float(request.data.get("age", 0))
            activity = str(
                request.data.get("activity_level", "")
            ).strip()
            weather = str(
                request.data.get("weather", "")
            ).strip()

            # Default hydration level filter
            hydration_level = "Good"

            # Filter data (case-insensitive)
            filtered = data[
                (data["Gender"].astype(str).str.lower() ==
                 gender.lower()) &
                (data["Physical Activity Level"]
                 .astype(str).str.lower() ==
                 activity.lower()) &
                (data["Weather"].astype(str).str.lower() ==
                 weather.lower()) &
                (data["Hydration Level"].astype(str).str.lower() ==
                 hydration_level.lower())
            ]

            # If no exact match found, use nearest weight + age
            if filtered.empty:

                pool = data[
                    data["Hydration Level"].astype(str).str.lower() ==
                    hydration_level.lower()
                ].copy()

                pool["difference"] = (
                    abs(pool["Weight (kg)"] - weight) +
                    abs(pool["Age"] - age)
                )

                nearest = pool.nsmallest(20, "difference")

                recommendation = round(
                    float(
                        nearest[
                            "Daily Water Intake (liters)"
                        ].mean()
                    ),
                    2
                )

                return Response({
                    "recommended_water_intake": recommendation,
                    "unit": "liters/day",
                    "note": "Based on nearest weight/age matches"
                })

            # Exact match found
            filtered = filtered.copy()

            filtered["difference"] = (
                abs(filtered["Weight (kg)"] - weight) +
                abs(filtered["Age"] - age)
            )

            nearest = filtered.nsmallest(20, "difference")

            recommendation = round(
                float(
                    nearest[
                        "Daily Water Intake (liters)"
                    ].mean()
                ),
                2
            )

            return Response({
                "recommended_water_intake": recommendation,
                "unit": "liters/day"
            })

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=500)