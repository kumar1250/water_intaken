from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
import pandas as pd


class WaterIntakeView(ViewSet):

    def post(self, request):

        try:
            # Load dataset
            data = pd.read_csv(r"d:\Daily_Water_Intake.csv")

            # Remove extra spaces from column names
            data.columns = data.columns.str.strip()

            gender = str(request.data.get("gender", "")).strip()
            weight = float(request.data.get("weight", 0))
            activity = str(
                request.data.get("activity_level", "")
            ).strip()
            weather = str(
                request.data.get("weather", "")
            ).strip()

            # Filter data (case-insensitive)
            filtered = data[
                (data["Gender"].astype(str).str.lower() ==
                 gender.lower()) &
                (data["Physical Activity Level"]
                 .astype(str).str.lower() ==
                 activity.lower()) &
                (data["Weather"].astype(str).str.lower() ==
                 weather.lower())
            ]

            # If no exact match found, use nearest weights
            if filtered.empty:

                data["difference"] = abs(
                    data["Weight (kg)"] - weight
                )

                nearest = data.nsmallest(20, "difference")

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
                    "note": "Based on nearest weight matches"
                })

            # Exact match found
            filtered = filtered.copy()

            filtered["difference"] = abs(
                filtered["Weight (kg)"] - weight
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