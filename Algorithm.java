import java.math.BigInteger;

public class Algorithm {
	public static void main(String[] args) {
		String[] Object = {"a", "b", "c"};
		
		int N = 1 << 3;
		
		for (int i=1; i<N; i++) {
			String n = String.format("%03d", new BigInteger(Integer.toBinaryString(i)));
			
			for (int j=0; j<3; j++) {
				if (n.charAt(j) == '1') {
					System.out.print(Object[j]);
				}
			}
			System.out.println();
		}
	}
}