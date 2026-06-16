export type AssessmentCreate = {
  jurisdiction: string;
  profile: {
    product_name: string;
    company_name?: string | null;
    intended_use: string;
    target_users: string[];
    jurisdictions: string[];
    delivery_model: 'web' | 'mobile' | 'desktop' | 'embedded' | 'api' | 'mixed';
    clinical_decision_support: boolean;
    provides_diagnosis: boolean;
    provides_treatment_recommendation: boolean;
    stores_phi: boolean;
    integrates_with_ehr: boolean;
    uses_ml_models: boolean;
    human_in_the_loop: boolean;
    software_lifecycle_stage: 'idea' | 'design' | 'prototype' | 'pre-market' | 'market';
  };
};
