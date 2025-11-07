#!/usr/bin/env python3
"""
Test IEEE preview functionality specifically
"""

import requests
import json
import sys

def test_ieee_preview():
    """Test IEEE document preview generation"""
    base_url = "https://format-a-python-backend.vercel.app"
    
    print("🧪 Testing IEEE Preview Generation")
    print(f"Base URL: {base_url}")
    
    # Test data for IEEE document
    test_data = {
        "title": "Advanced Machine Learning Techniques for Real-Time Data Processing",
        "authors": [
            {
                "name": "Dr. John Smith",
                "email": "john.smith@university.edu",
                "affiliation": "Department of Computer Science, Tech University"
            },
            {
                "name": "Prof. Jane Doe", 
                "email": "jane.doe@research.org",
                "affiliation": "AI Research Institute"
            }
        ],
        "abstract": "This paper presents novel machine learning techniques for processing large-scale real-time data streams. We introduce a hybrid approach combining deep neural networks with traditional statistical methods to achieve superior performance in dynamic environments. Our experimental results demonstrate significant improvements in accuracy and processing speed compared to existing state-of-the-art methods.",
        "keywords": "machine learning, real-time processing, neural networks, data streams, performance optimization",
        "sections": [
            {
                "title": "Introduction",
                "content": "The rapid growth of data generation in modern applications has created unprecedented challenges for real-time processing systems. Traditional approaches often fail to maintain accuracy while meeting strict latency requirements. This work addresses these challenges by proposing a novel hybrid architecture that combines the representational power of deep learning with the computational efficiency of classical statistical methods."
            },
            {
                "title": "Related Work",
                "content": "Previous research in real-time machine learning has focused primarily on either accuracy optimization or latency reduction, but rarely both simultaneously. Smith et al. (2023) proposed a streaming algorithm that achieves low latency but sacrifices accuracy for complex patterns. In contrast, our approach maintains high accuracy while meeting real-time constraints through innovative architectural design."
            },
            {
                "title": "Methodology",
                "content": "Our hybrid approach consists of three main components: (1) a lightweight feature extraction module using convolutional neural networks, (2) a statistical pattern recognition engine for rapid classification, and (3) an adaptive fusion mechanism that dynamically weights the contributions of each component based on data characteristics and performance requirements."
            },
            {
                "title": "Experimental Results",
                "content": "We evaluated our approach on three benchmark datasets: StreamData-1K, RealTime-ML, and Industrial-IoT. Results show consistent improvements across all metrics: 15% increase in accuracy, 40% reduction in processing latency, and 25% improvement in memory efficiency compared to baseline methods. The adaptive fusion mechanism proved particularly effective in handling concept drift scenarios."
            },
            {
                "title": "Conclusion",
                "content": "This work demonstrates that hybrid architectures can successfully bridge the gap between accuracy and efficiency in real-time machine learning applications. Future work will explore the application of these techniques to distributed computing environments and investigate their scalability to even larger data volumes."
            }
        ],
        "references": [
            {
                "text": "Smith, A., Johnson, B., and Williams, C. (2023). 'Efficient Streaming Algorithms for Large-Scale Data Processing,' IEEE Transactions on Big Data, vol. 9, no. 2, pp. 123-135."
            },
            {
                "text": "Zhang, L., Kumar, R., and Anderson, M. (2022). 'Deep Learning Approaches for Real-Time Analytics,' Journal of Machine Learning Research, vol. 23, pp. 1456-1478."
            },
            {
                "text": "Brown, D. and Lee, S. (2023). 'Hybrid Neural-Statistical Models for Dynamic Environments,' Proceedings of the International Conference on Machine Learning, pp. 234-248."
            },
            {
                "text": "Taylor, K., Martinez, P., and Chen, W. (2022). 'Performance Optimization in Streaming Machine Learning Systems,' ACM Computing Surveys, vol. 54, no. 8, pp. 1-32."
            }
        ]
    }
    
    try:
        print("\n📄 Sending IEEE document generation request...")
        response = requests.post(f"{base_url}/api/document-generator", 
                               json=test_data, 
                               timeout=30,
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ IEEE Preview Generation Successful!")
                print(f"Success: {data.get('success', False)}")
                print(f"Preview Type: {data.get('preview_type', 'unknown')}")
                print(f"Message: {data.get('message', 'No message')}")
                
                # Check if HTML preview is generated
                if data.get('html_content'):
                    html_length = len(data['html_content'])
                    print(f"📄 HTML Preview Generated: {html_length} characters")
                    
                    # Save preview to file for inspection
                    with open('ieee_preview_sample.html', 'w', encoding='utf-8') as f:
                        f.write(data['html_content'])
                    print("💾 Preview saved to: ieee_preview_sample.html")
                    
                    # Check if preview contains expected IEEE elements
                    html_content = data['html_content'].lower()
                    ieee_elements = [
                        'ieee-title',
                        'ieee-authors', 
                        'abstract',
                        'keywords',
                        'introduction',
                        'references'
                    ]
                    
                    found_elements = [elem for elem in ieee_elements if elem in html_content]
                    print(f"🔍 IEEE Elements Found: {len(found_elements)}/{len(ieee_elements)}")
                    print(f"   Elements: {', '.join(found_elements)}")
                    
                    if len(found_elements) >= 4:
                        print("✅ IEEE Preview contains proper formatting!")
                        return True
                    else:
                        print("⚠️  IEEE Preview may be missing some elements")
                        return False
                else:
                    print("❌ No HTML content in response")
                    return False
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                print(f"Response: {response.text[:500]}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 IEEE Preview Functionality Test")
    print("=" * 50)
    
    success = test_ieee_preview()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 IEEE Preview Test PASSED!")
        print("✅ Python backend IEEE preview is working correctly")
        print("✅ Preview is publicly accessible via Vercel")
        print("✅ HTML formatting includes proper IEEE elements")
        return 0
    else:
        print("❌ IEEE Preview Test FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())