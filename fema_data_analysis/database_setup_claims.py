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
    "crsClassCode": "Int16",              # v3 rename: was crsClassificationCode
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
    "numberOfUnits": "Int32",             # v3 goes up to 99999 (Int16 caps at 32767)
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
    "censusGeoid": "string",              # v3 rename: replaces censusTract + censusBlockGroupFips
    "id": "string",

    # --- Fields new in v3 -------------------------------------------------
    "foundationType": "category",
    "preFirmIndicator": "boolean",

    # v3 splits the old single waterDepth into exterior/interior.
    # If the cast ever complains, these hold decimals -> switch to "float64".
    "exteriorWaterDepth": "Int16",
    "interiorWaterDepth": "Int16",

    # Recovery / subrogation amounts (dollars, as with the amountPaidOn* fields)
    "totalSalvageRecovery": "float64",
    "totalBldgClaimPmtRecovery": "float64",
    "totalContentsClaimPmtRecovery": "float64",
    "totalIccClaimPmtRecovery": "float64",
    "totalSubrogationRecovery": "float64"
}

# Date/datetime columns to parse separately
claims_date_cols = [
    "asOfDate",
    "dateOfLoss",
    "originalConstructionDate",
    "originalNBDate",

    # New in v3
    "openDate",
    "mostRecentPaymentDate",
    "mostRecentRecoveryDate"
]