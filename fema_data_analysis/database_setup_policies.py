policies_dtype_dict = {
    # Boolean fields - use boolean (pandas nullable boolean)
    "agricultureStructureIndicator": "boolean",
    "construction": "boolean", 
    "elevatedBuildingIndicator": "boolean",
    "houseOfWorshipIndicator": "boolean",
    "nonProfitIndicator": "boolean",
    "postFIRMConstructionIndicator": "boolean",
    "primaryResidenceIndicator": "boolean",
    "smallBusinessIndicatorBuilding": "boolean",
    "postFirmVzoneIndicator": "boolean",
    "floodproofedIndicator": "boolean",
    "rentalPropertyIndicator": "boolean",
    "tenantIndicator": "boolean",
    "stateOwnedIndicator": "boolean",
    "mandatoryPurchaseFlag": "boolean",
    "programTypeIndicator": "boolean",
    
    # Decimal/Float fields - use float64 for precision
    "baseFloodElevation": "float64",
    "lowestAdjacentGrade": "float64", 
    "lowestFloorElevation": "float64",
    "basicBuildingRate": "float64",
    "additionalBuildingRate": "float64",
    "basicContentsRate": "float64",
    "additionalContentsRate": "float64",  # v3 fixed the capital A that v2 had
    "latitude": "float64",
    "longitude": "float64",
    
    # Integer fields - use appropriate nullable integer types
    "basementEnclosureCrawlspaceType": "Int16",
    "elevationDifference": "Int32",
    "federalPolicyFee": "Int16", 
    "hfiaaSurcharge": "Int16",
    "locationOfContents": "Int16",
    "numberOfFloorsInInsuredBuilding": "Int16",
    "obstructionType": "Int16",
    "occupancyType": "Int16",
    "policyCost": "Int32",
    "policyCount": "Int16",
    "policyTermIndicator": "Int16",
    "totalBuildingInsuranceCoverage": "Int32",
    "totalContentsInsuranceCoverage": "Int32", 
    "totalInsurancePremiumOfThePolicy": "Int32",
    "iccPremium": "Int16",
    "reserveFundAssessment": "Int32",
    "communityProbationSurcharge": "Int16",
    "premiumPaymentIndicator": "Int16",
    "buildingDescriptionCode": "Int16",
    "insuranceToValueCode": "Int16",
    "disasterAssistanceCoverageRequiredCode": "Int16",
    "grandfatheringTypeCode": "Int16",
    "femaRegion": "Int16",
    
    # Large integer fields
    "buildingReplacementCost": "Int64",
    
    # Text/String fields - use category for low cardinality, string for high cardinality
    "condominiumCoverageTypeCode": "category",
    "crsClassCode": "Int16", 
    "buildingDeductibleCode": "category",
    "contentsDeductibleCode": "category", 
    "elevationCertificateIndicator": "category",
    "ratedFloodZone": "category",
    "rateMethod": "category",
    "regularEmergencyProgramIndicator": "category",
    "cancellationVoidanceReasonCode": "category",
    "subsidizedRateType": "category",
    "enclosureTypeCode": "category",
    "waitingPeriodType": "category",
    "rolloverTransferCode": "category",
    "nfipRatedCommunityNumber": "string",
    "nfipCommunityNumberCurrent": "string", 
    "nfipCommunityName": "string",
    "mapPanelNumber": "string",
    "mapPanelSuffix": "string",
    "floodZoneCurrent": "category",
    "propertyState": "category",
    "reportedCity": "string",
    "reportedZipCode": "string",
    # countyCode is gone in v3 policies -- derive it from censusGeoid[:5] if needed
    "censusGeoid": "string",              # v3 rename: replaces censusTract + censusBlockGroupFips
    "id": "string",

    # --- Fields new in v3 -------------------------------------------------
    "fullRiskPremium": "float64",
    "preFIRMConstructionIndicator": "boolean",

    # Codes whose exact form I could not verify -- category is safe for any of
    # them. Switch to "boolean" if you confirm one is a simple true/false flag.
    "buildingOnFederalLand": "category",
    "buildingPurpose": "category",
    "buildingOverWaterType": "category",
    "seasonallyOccupied": "category",
    "foundationType": "category"
}

# Date columns to parse separately
policies_date_cols = [
    "asOfDate",                           # new in v3
    "cancellationDateOfFloodPolicy",
    "originalConstructionDate", 
    "originalNBDate",
    "policyEffectiveDate",
    "policyTerminationDate",
    "endorsementEffectiveDate",
    "propertyPurchaseDate"
]