claims_dtype_dict = {
    # Boolean fields - use boolean (pandas nullable boolean)
    "agricultureStructureIndicator": "boolean",
    "elevatedBuildingIndicator": "boolean", 
    "houseWorship": "boolean",
    "nonProfitIndicator": "boolean",
    "postFIRMConstructionIndicator": "boolean",
    "smallBusinessIndicatorBuilding": "boolean",
    "primaryResidenceIndicator": "boolean",
    "floodproofedIndicator": "boolean",
    "stateOwnedIndicator": "boolean",
    "rentalPropertyIndicator": "boolean",
    
    # Decimal/Float fields - use float64 for precision
    "baseFloodElevation": "float64",
    "lowestAdjacentGrade": "float64",
    "lowestFloorElevation": "float64", 
    "amountPaidOnBuildingClaim": "float64",
    "amountPaidOnContentsClaim": "float64",
    "amountPaidOnIncreasedCostOfComplianceClaim": "float64",
    "netBuildingPaymentAmount": "float64",
    "netContentsPaymentAmount": "float64",
    "netIccPaymentAmount": "float64",
    "latitude": "float64",
    "longitude": "float64",

    # Integer fields - use appropriate nullable integer types
    "basementEnclosureCrawlspaceType": "Int16",
    "policyCount": "Int16",
    "crsClassificationCode": "Int16",
    "elevationDifference": "Int32",
    "locationOfContents": "Int16", 
    "numberOfFloorsInTheInsuredBuilding": "Int16",
    "obstructionType": "Int16",
    "occupancyType": "Int16",
    "totalBuildingInsuranceCoverage": "Int32",
    "totalContentsInsuranceCoverage": "Int32",
    "yearOfLoss": "Int16",
    "buildingDamageAmount": "Int32",
    "buildingPropertyValue": "Int32",
    "contentsDamageAmount": "Int32",
    "contentsPropertyValue": "Int32", 
    "disasterAssistanceCoverageRequired": "Int16",
    "ficoNumber": "Int16",
    "floodCharacteristicsIndicator": "Int16",
    "floodWaterDuration": "Int16",
    "iccCoverage": "Int32",
    "numberOfUnits": "Int16",
    "contentsReplacementCost": "Int32",
    "waterDepth": "Int16",
    "buildingDescriptionCode": "Int16",
    
    # Large integer fields
    "buildingReplacementCost": "Int64",
    
    # Text/String fields - use category for low cardinality, string for high cardinality
    "elevationCertificateIndicator": "category",
    "ratedFloodZone": "category",
    "rateMethod": "category", 
    "buildingDeductibleCode": "category",
    "causeOfDamage": "category",
    "condominiumCoverageTypeCode": "category",
    "contentsDeductibleCode": "category",
    "eventDesignationNumber": "string",
    "floodEvent": "string",
    "nfipRatedCommunityNumber": "string",
    "nfipCommunityNumberCurrent": "string",
    "nfipCommunityName": "string", 
    "nonPaymentReasonContents": "category",
    "nonPaymentReasonBuilding": "category",
    "replacementCostBasis": "category",
    "floodZoneCurrent": "category",
    "state": "category",
    "reportedCity": "string", 
    "reportedZipCode": "string",
    "countyCode": "string",
    "censusTract": "string",
    "censusBlockGroupFips": "string",
    "id": "string"
}

# Date/datetime columns to parse separately
claims_date_cols = [
    "asOfDate",
    "dateOfLoss",
    "originalConstructionDate",
    "originalNBDate"
]