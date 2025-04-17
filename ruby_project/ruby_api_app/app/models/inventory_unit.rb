# class InventoryUnit
#   include Mongoid::Document
#   include Mongoid::Timestamps
#   field :created_at, type: Time
#   field :batch_id, type: String
# end



# class InventoryUnit
#   include Mongoid::Document
#   include Mongoid::Timestamps

#   field :batch_id, type: String
# end

class InventoryUnit
  include Mongoid::Document
  include Mongoid::Timestamps

  field :batch_id, type: String
  field :price, type: Float
  field :quantity, type: Integer
end
