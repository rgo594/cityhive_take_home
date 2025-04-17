class InventoryUnitsController < ApplicationController
    def create
      batch_id = SecureRandom.uuid
  
      units = params[:inventory_units].map do |unit_params|
        InventoryUnit.create!(unit_params.merge(batch_id: batch_id))
      end
  
      render json: units, status: :created
    end
  end