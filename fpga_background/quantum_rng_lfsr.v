// Simple 8-bit LFSR for pseudo-random sequence demonstration
module quantum_rng_lfsr(
    input wire clk,
    input wire rst,
    output reg [7:0] rnd
);
    wire feedback = rnd[7] ^ rnd[5] ^ rnd[4] ^ rnd[3];

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            rnd <= 8'hA5; // non-zero seed
        end else begin
            rnd <= {rnd[6:0], feedback};
        end
    end
endmodule
