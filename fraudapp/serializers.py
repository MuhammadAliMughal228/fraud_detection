from rest_framework import serializers

class JSONResponseSerializer(serializers.Serializer):
    json_data = serializers.JSONField()

class PieRecordsSerializer(serializers.Serializer):
    pie_labels = serializers.ListField(
        child=serializers.CharField()
    )
    pie_values = serializers.ListField(
        child=serializers.IntegerField()
    )

class ChartDataSerializer(serializers.Serializer):
    labels = serializers.ListField(
        child=serializers.CharField()
    )
    values = serializers.ListField(
        child=serializers.IntegerField()
    )

class LineChartSerializer(serializers.Serializer):
    labels = serializers.ListField(
        child=serializers.CharField()
    )
    values = serializers.ListField(
        child=serializers.FloatField()
    )

class HistogramSerializer(serializers.Serializer):
    bins = serializers.ListField(
        child=serializers.CharField()
    )
    values = serializers.ListField(
        child=serializers.IntegerField()
    )

class HeatMapProceedSerializer(serializers.Serializer):
    bins = serializers.ListField(
        child=serializers.CharField()
    )
    values = serializers.ListField(
        child=serializers.IntegerField()
    )

class BoxPlotDataSerializer(serializers.Serializer):
    InitialApprovalAmount = serializers.FloatField()
    ForgivenessAmount = serializers.FloatField()
    PROCEED_Per_Job = serializers.FloatField()

class BoxPlotSerializer(serializers.Serializer):
    box_plot_data = BoxPlotDataSerializer()

class ScatterPlotSerializer(serializers.Serializer):
    x = serializers.ListField(
        child=serializers.FloatField()
    )
    y = serializers.ListField(
        child=serializers.FloatField()
    )



class BarChartRecordSerializer(serializers.Serializer):
    pie_records = PieRecordsSerializer()
    loan_status = ChartDataSerializer()
    borrower_state = ChartDataSerializer()
    business_type = ChartDataSerializer()
    race = ChartDataSerializer()
    ethnicity = ChartDataSerializer()
    gender = ChartDataSerializer()
    veteran = ChartDataSerializer()
    line_chart_approval = LineChartSerializer()
    line_chart_forgiveness = LineChartSerializer()
    histogram_initial = HistogramSerializer()
    histogram_forgiveness = HistogramSerializer()
    histogram_proceed = HistogramSerializer()
    HeatMapProceed = HeatMapProceedSerializer()
 
class barser(serializers.Serializer):
    p = serializers.CharField()

class FraudPredictionSerializer(serializers.Serializer):
    LoanNumber = serializers.FloatField()
    DateApproved = serializers.FloatField()
    SBAOfficeCode = serializers.FloatField()
    ProcessingMethod = serializers.FloatField()
    BorrowerName = serializers.FloatField()
    BorrowerAddress = serializers.FloatField()
    BorrowerCity = serializers.FloatField()
    BorrowerState = serializers.FloatField()
    BorrowerZip = serializers.FloatField()
    LoanStatusDate = serializers.FloatField()
    LoanStatus = serializers.FloatField()
    Term = serializers.FloatField()
    SBAGuarantyPercentage = serializers.FloatField()
    InitialApprovalAmount = serializers.FloatField()
    CurrentApprovalAmount = serializers.FloatField()
    UndisbursedAmount = serializers.FloatField()
    FranchiseName = serializers.FloatField()
    ServicingLenderLocationID = serializers.FloatField()
    ServicingLenderName = serializers.FloatField()
    ServicingLenderAddress = serializers.FloatField()
    ServicingLenderCity = serializers.FloatField()
    ServicingLenderState = serializers.FloatField()
    ServicingLenderZip = serializers.FloatField()
    RuralUrbanIndicator = serializers.FloatField()
    HubzoneIndicator = serializers.FloatField()
    LMIIndicator = serializers.FloatField()
    BusinessAgeDescription = serializers.FloatField()
    ProjectCity = serializers.FloatField()
    ProjectCountyName = serializers.FloatField()
    ProjectState = serializers.FloatField()
    ProjectZip = serializers.FloatField()
    CD = serializers.FloatField()
    JobsReported = serializers.FloatField()
    NAICSCode = serializers.FloatField()
    Race = serializers.FloatField()
    Ethnicity = serializers.FloatField()
    UTILITIES_PROCEED = serializers.FloatField()
    PAYROLL_PROCEED = serializers.FloatField()
    MORTGAGE_INTEREST_PROCEED = serializers.FloatField()
    RENT_PROCEED = serializers.FloatField()
    REFINANCE_EIDL_PROCEED = serializers.FloatField()
    HEALTH_CARE_PROCEED = serializers.FloatField()
    DEBT_INTEREST_PROCEED = serializers.FloatField()
    BusinessType = serializers.FloatField()
    OriginatingLenderLocationID = serializers.FloatField()
    OriginatingLender = serializers.FloatField()
    OriginatingLenderCity = serializers.FloatField()
    OriginatingLenderState = serializers.FloatField()
    Gender = serializers.FloatField()
    Veteran = serializers.FloatField()
    NonProfit = serializers.FloatField()
    ForgivenessAmount = serializers.FloatField()
    ForgivenessDate = serializers.FloatField()
    ApprovalDiff = serializers.FloatField()
    NotForgivenAmount = serializers.FloatField()
    ForgivenPercentage = serializers.FloatField()
    TOTAL_PROCEED = serializers.FloatField()
    PROCEED_Diff = serializers.FloatField()
    UTILITIES_PROCEED_pct = serializers.FloatField()
    PAYROLL_PROCEED_pct = serializers.FloatField()
    MORTGAGE_INTEREST_PROCEED_pct = serializers.FloatField()
    RENT_PROCEED_pct = serializers.FloatField()
    REFINANCE_EIDL_PROCEED_pct = serializers.FloatField()
    HEALTH_CARE_PROCEED_pct = serializers.FloatField()
    DEBT_INTEREST_PROCEED_pct = serializers.FloatField()
    PROCEED_Per_Job = serializers.FloatField()

class InputSerializer(serializers.Serializer):
    data = serializers.JSONField(required=False)
    text = serializers.CharField(required=False)
    
    def validate(self, attrs):
        if not attrs.get('data') and not attrs.get('text'):
            raise serializers.ValidationError("Either 'data' or 'text' must be provided.")
        return attrs

class FrequencySerializer(serializers.Serializer):
    state_counts = serializers.DictField(child=serializers.IntegerField())
    city_counts = serializers.DictField(child=serializers.IntegerField())


class ForgivenessDataSerializer(serializers.Serializer):
    ForgivenessDate = serializers.DateField()
    ForgivenessAmount = serializers.FloatField()

class GraphsSerializer(serializers.Serializer):
    top5_states = serializers.DictField(child=serializers.IntegerField())
    value_counts_arrays_specific = serializers.DictField(child=serializers.ListField(child=serializers.IntegerField()))
    bar_data = serializers.ListField(child=ForgivenessDataSerializer())
    line_data = serializers.ListField(child=ForgivenessDataSerializer())
