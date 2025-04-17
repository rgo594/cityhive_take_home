class InventoryUploadsController < ApplicationController
    def create
        batch_id = SecureRandom.uuid
        units = params[:inventory_units].map do |unit|
            InventoryUnit.create!(
                unit.permit(
                :price,
                :quantity,
                :upc,
                :internal_id,
                :department,
                :name,
                :properties,
                :tags,
                :last_sold
                ).merge(batch_id: batch_id)
            )
        end          
  
      render json: { message: "Batch created", batch_id: batch_id }, status: :created
    end
  
    def index
      grouped = InventoryUnit.collection.aggregate([
        { "$group": {
          _id: "$batch_id",
          number_of_units: { "$sum": 1 },
          average_price: { "$avg": "$price" },
          total_quantity: { "$sum": "$quantity" }
        }}
      ])
  
      result = grouped.map do |doc|
        {
          batch_id: doc["_id"],
          number_of_units: doc["number_of_units"],
          average_price: doc["average_price"]&.round(2),
          total_quantity: doc["total_quantity"]
        }
      end
  
      render json: result
    end
  end