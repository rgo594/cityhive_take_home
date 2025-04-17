class InventoryUnit
  include Mongoid::Document
  include Mongoid::Timestamps

  field :price, type: Float
  field :quantity, type: Float
  field :upc, type: String
  field :internal_id, type: String
  field :department, type: String
  field :name, type: String
  field :properties, type: Hash
  field :tags, type: Array
  field :last_sold, type: String
  field :batch_id, type: String
end